"""
Controller: intermediario entre la interfaz de usuario y la base de datos PostgreSQL.

Ofrece las operaciones de la aplicación mediante consultas SQL nativas (psycopg2):
- crear_tablas / borrar_tablas (DDL y carga de catálogo)
- insertar_caso               (INSERT INTO ... RETURNING)
- buscar_casos                (SELECT con ILIKE)
- buscar_caso_por_id          (SELECT por clave primaria)
- listar_casos                (SELECT ordenado por id descendente)
- calcular_caso               (Cálculo sin persistencia)

Todas las fallas de la base de datos se encapsulan como ``BaseDeDatosError``
para que las capas de presentación (Web, GUI, Consola) puedan capturarlas
sin depender de los detalles técnicos del controlador.
"""

from collections.abc import Callable
from typing import Any

from src.database.conexion import (
    DIRECTORIO_SQL,
    ejecutar_script_sql,
    obtener_conexion,
)
from src.model.incapacidad import (
    TIPOS_INCAPACIDAD,
    IncapacidadError,
    calcular_pago_incapacidad,
    obtener_porcentaje_reconocimiento,
)

FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


class BaseDeDatosError(IncapacidadError):
    """Indica que una operación con la base de datos falló."""

    def __init__(self, operacion: str, detalle: object) -> None:
        causa = (str(detalle).splitlines() or [""])[0][:150]
        super().__init__(
            f"Error: no se pudo {operacion} en la base de datos. "
            f"Verifique que las tablas existan y que la conexión "
            f"sea correcta. ({type(detalle).__name__}: {causa})"
        )


class DiasNoEnteros(IncapacidadError):
    """Indica que los días de incapacidad no son un número entero."""

    def __init__(self, dias: float) -> None:
        super().__init__(
            f"Error: los días de incapacidad deben ser un número entero (recibido: {dias})."
        )


class CasoNoEncontrado(IncapacidadError):
    """Indica que no existe un caso con el ID solicitado."""

    def __init__(self, id_caso: int) -> None:
        super().__init__(f"Error: no existe un caso con ID {id_caso}.")


class BusquedaInvalida(IncapacidadError):
    """Indica que el texto de búsqueda está vacío o no es texto."""

    def __init__(self) -> None:
        super().__init__("Error: escriba un texto para buscar (ID, fecha o tipo).")


def _nombre_tipo(clave: str) -> str:
    """Convierte 'enfermedad_general' en 'Enfermedad General'."""
    return clave.replace("_", " ").title()


class IncapacidadController:
    """Controller de casos de incapacidad sobre PostgreSQL."""

    def __init__(
        self,
        conexion_factory: Callable[[], Any] | None = None,
    ) -> None:
        """
        Inicializa el controlador.

        Args:
            conexion_factory: Fábrica opcional que retorna una conexión a la BD.
                Si es None, se utiliza `obtener_conexion()` de `src.database.conexion`.
        """
        self._conexion_factory = conexion_factory

    def _conectar(self) -> Any:
        """Abre y retorna una nueva conexión a la base de datos."""
        if self._conexion_factory is not None:
            return self._conexion_factory()
        return obtener_conexion()

    @staticmethod
    def _fila_a_diccionario(fila: tuple) -> dict:
        """Convierte una tupla de consulta SQL en el diccionario estándar de caso."""
        id_caso, fecha, clave, nombre, salario, dias, pago = fila
        if hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime(FORMATO_FECHA)
        else:
            fecha_str = str(fecha)[:19]

        return {
            "id": id_caso,
            "fecha": fecha_str,
            "tipo_incapacidad": clave,
            "tipo_nombre": nombre,
            "salario": float(salario),
            "dias": int(dias),
            "pago": float(pago),
        }

    # ----------------------------------------------------------
    # CREAR / BORRAR TABLAS
    # ----------------------------------------------------------

    def crear_tablas(self) -> None:
        """
        Crea las tablas en PostgreSQL si no existen y puebla el catálogo inicial.
        Es seguro invocar este método varias veces.
        """
        scripts = [
            "crear-tipos-incapacidad.sql",
            "datos-tipos-incapacidad.sql",
            "crear-casos-incapacidad.sql",
        ]
        conexion = None
        try:
            conexion = self._conectar()
            for nombre_script in scripts:
                ruta = DIRECTORIO_SQL / nombre_script
                ejecutar_script_sql(ruta, conexion=conexion)
            conexion.commit()
        except Exception as error:
            if conexion:
                conexion.rollback()
            raise BaseDeDatosError("crear las tablas", error) from error
        finally:
            if conexion:
                conexion.close()

    def borrar_tablas(self) -> None:
        """Elimina las tablas de la base de datos PostgreSQL."""
        ruta = DIRECTORIO_SQL / "borrar-tablas.sql"
        conexion = None
        try:
            conexion = self._conectar()
            ejecutar_script_sql(ruta, conexion=conexion)
            conexion.commit()
        except Exception as error:
            if conexion:
                conexion.rollback()
            raise BaseDeDatosError("borrar las tablas", error) from error
        finally:
            if conexion:
                conexion.close()

    # ----------------------------------------------------------
    # INICIALIZACIÓN
    # ----------------------------------------------------------

    def inicializar_bd(self) -> None:
        """
        Verifica la conectividad con PostgreSQL y crea las tablas si no existen.
        Si la base de datos no está disponible al iniciar, se omite silenciosamente
        para permitir que la interfaz arranque y notifique errores al ejecutar acciones.
        """
        try:
            self.crear_tablas()
        except Exception:
            pass

    def inicializar_con_fallback(self) -> None:
        """Alias para inicializar_bd para mantener compatibilidad."""
        self.inicializar_bd()

    # ----------------------------------------------------------
    # INSERTAR
    # ----------------------------------------------------------

    def insertar_caso(
        self,
        salario: float,
        dias: float,
        tipo_incapacidad: str = "enfermedad_general",
    ) -> dict:
        """
        Calcula el valor a pagar y guarda el caso en PostgreSQL.

        Returns:
            Diccionario con el caso guardado (id, fecha, tipo, salario, dias, pago).

        Raises:
            IncapacidadError: Si los datos de entrada son inválidos o los días no son enteros.
            BaseDeDatosError: Si ocurre un fallo en PostgreSQL.
        """
        pago = calcular_pago_incapacidad(
            salario_mensual=salario,
            dias_incapacidad=dias,
            tipo_incapacidad=tipo_incapacidad,
        )

        if dias != int(dias):
            raise DiasNoEnteros(dias)

        conexion = None
        try:
            conexion = self._conectar()
            with conexion.cursor() as cursor:
                # 1. Obtener ID y nombre descriptivo del tipo de incapacidad
                cursor.execute(
                    "SELECT id, nombre FROM tipos_incapacidad WHERE clave = %s;",
                    (tipo_incapacidad,),
                )
                fila_tipo = cursor.fetchone()
                if not fila_tipo:
                    raise ValueError(
                        f"El tipo de incapacidad '{tipo_incapacidad}' no está registrado en la base de datos."
                    )
                tipo_id, tipo_nombre = fila_tipo[0], fila_tipo[1]

                # 2. Insertar el caso y obtener el ID y fecha asignados
                consulta_insert = """
                INSERT INTO casos_incapacidad (fecha, tipo_id, salario, dias, pago)
                VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s)
                RETURNING id, fecha;
                """
                cursor.execute(
                    consulta_insert,
                    (tipo_id, salario, int(dias), pago),
                )
                nuevo_id, fecha = cursor.fetchone()

            conexion.commit()

            if hasattr(fecha, "strftime"):
                fecha_str = fecha.strftime(FORMATO_FECHA)
            else:
                fecha_str = str(fecha)[:19]

            return {
                "id": nuevo_id,
                "fecha": fecha_str,
                "tipo_incapacidad": tipo_incapacidad,
                "tipo_nombre": tipo_nombre,
                "salario": float(salario),
                "dias": int(dias),
                "pago": float(pago),
            }
        except IncapacidadError:
            if conexion:
                conexion.rollback()
            raise
        except Exception as error:
            if conexion:
                conexion.rollback()
            raise BaseDeDatosError("guardar el caso", error) from error
        finally:
            if conexion:
                conexion.close()

    # ----------------------------------------------------------
    # CONSULTAS (SELECT)
    # ----------------------------------------------------------

    def listar_casos(self) -> list[dict]:
        """Retorna todos los casos registrados en orden descendente por ID."""
        consulta = """
        SELECT c.id, c.fecha, t.clave, t.nombre, c.salario, c.dias, c.pago
        FROM casos_incapacidad c
        JOIN tipos_incapacidad t ON c.tipo_id = t.id
        ORDER BY c.id DESC;
        """
        conexion = None
        try:
            conexion = self._conectar()
            with conexion.cursor() as cursor:
                cursor.execute(consulta)
                filas = cursor.fetchall()
            return [self._fila_a_diccionario(fila) for fila in filas]
        except Exception as error:
            raise BaseDeDatosError("consultar los casos", error) from error
        finally:
            if conexion:
                conexion.close()

    def buscar_casos(self, texto: str) -> list[dict]:
        """
        Busca casos cuyo ID, fecha, clave o nombre de tipo coincidan con el texto.

        Raises:
            BusquedaInvalida: Si el texto está vacío o no es una cadena.
            BaseDeDatosError: Si ocurre un fallo en PostgreSQL.
        """
        if not isinstance(texto, str) or not texto.strip():
            raise BusquedaInvalida()

        patron = f"%{texto.strip()}%"
        consulta = """
        SELECT c.id, c.fecha, t.clave, t.nombre, c.salario, c.dias, c.pago
        FROM casos_incapacidad c
        JOIN tipos_incapacidad t ON c.tipo_id = t.id
        WHERE CAST(c.id AS TEXT) ILIKE %s
           OR CAST(c.fecha AS TEXT) ILIKE %s
           OR t.nombre ILIKE %s
           OR t.clave ILIKE %s
        ORDER BY c.id DESC;
        """
        conexion = None
        try:
            conexion = self._conectar()
            with conexion.cursor() as cursor:
                cursor.execute(consulta, (patron, patron, patron, patron))
                filas = cursor.fetchall()
            return [self._fila_a_diccionario(fila) for fila in filas]
        except Exception as error:
            raise BaseDeDatosError("buscar los casos", error) from error
        finally:
            if conexion:
                conexion.close()

    def buscar_caso_por_id(self, id_caso: int) -> dict:
        """
        Busca un caso específico por su ID.

        Raises:
            CasoNoEncontrado: Si no existe un caso con ese ID.
            BaseDeDatosError: Si ocurre un fallo en PostgreSQL.
        """
        consulta = """
        SELECT c.id, c.fecha, t.clave, t.nombre, c.salario, c.dias, c.pago
        FROM casos_incapacidad c
        JOIN tipos_incapacidad t ON c.tipo_id = t.id
        WHERE c.id = %s;
        """
        conexion = None
        try:
            conexion = self._conectar()
            with conexion.cursor() as cursor:
                cursor.execute(consulta, (id_caso,))
                fila = cursor.fetchone()
            if not fila:
                raise CasoNoEncontrado(id_caso)
            return self._fila_a_diccionario(fila)
        except IncapacidadError:
            raise
        except Exception as error:
            raise BaseDeDatosError("buscar el caso por ID", error) from error
        finally:
            if conexion:
                conexion.close()

    # ----------------------------------------------------------
    # CÁLCULO SIN PERSISTENCIA
    # ----------------------------------------------------------

    def calcular_caso(
        self,
        salario: float,
        dias: float,
        tipo_incapacidad: str = "enfermedad_general",
    ) -> dict:
        """
        Calcula el pago de una incapacidad sin guardarla en la base de datos.

        Returns:
            Diccionario con salario, dias, tipo_incapacidad, porcentaje y pago.

        Raises:
            IncapacidadError: Si los datos de entrada no son válidos.
        """
        pago = calcular_pago_incapacidad(
            salario_mensual=salario,
            dias_incapacidad=dias,
            tipo_incapacidad=tipo_incapacidad,
        )
        porcentaje = obtener_porcentaje_reconocimiento(tipo_incapacidad)

        return {
            "salario": salario,
            "dias": dias,
            "tipo_incapacidad": tipo_incapacidad,
            "porcentaje": porcentaje,
            "pago": pago,
        }
