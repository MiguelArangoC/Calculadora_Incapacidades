"""
Controller: intermediario entre la interfaz de usuario y la base de datos.

Ofrece las operaciones de la aplicación:

- crear_tablas / borrar_tablas
- insertar_caso            (INSERT INTO)
- buscar_casos / buscar_caso_por_id / listar_casos   (SELECT)

Todas las fallas de la base de datos se reportan como
``BaseDeDatosError`` para que la interfaz las muestre sin conocer
SQLAlchemy.
"""

from sqlalchemy import Engine, String, cast, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.conexion import RUTA_SQLITE_POR_DEFECTO, obtener_engine
from src.model.incapacidad import (
    TIPOS_INCAPACIDAD,
    IncapacidadError,
    calcular_pago_incapacidad,
    obtener_porcentaje_reconocimiento,
)
from src.model.orm import Base, CasoIncapacidad, TipoIncapacidad


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
            "Error: los días de incapacidad deben ser un número "
            f"entero (recibido: {dias})."
        )


class CasoNoEncontrado(IncapacidadError):
    """Indica que no existe un caso con el ID solicitado."""

    def __init__(self, id_caso: int) -> None:
        super().__init__(
            f"Error: no existe un caso con ID {id_caso}."
        )


class BusquedaInvalida(IncapacidadError):
    """Indica que el texto de búsqueda está vacío o no es texto."""

    def __init__(self) -> None:
        super().__init__(
            "Error: escriba un texto para buscar (ID, fecha o tipo)."
        )


def _nombre_tipo(clave: str) -> str:
    """'enfermedad_general' -> 'Enfermedad General'."""
    return clave.replace("_", " ").title()


class IncapacidadController:
    """Controller de casos de incapacidad."""

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine

    @property
    def engine(self) -> Engine:
        """Engine en uso (el de secret_config si no se inyectó otro)."""
        if self._engine is None:
            self._engine = obtener_engine()
        return self._engine

    # ----------------------------------------------------------
    # CREAR / BORRAR TABLAS
    # ----------------------------------------------------------

    def crear_tablas(self) -> None:
        """
        Crea las tablas si no existen y carga el catálogo de tipos.

        Es seguro llamarla varias veces.
        """
        try:
            Base.metadata.create_all(self.engine)

            with Session(self.engine) as sesion:
                existentes = set(
                    sesion.scalars(select(TipoIncapacidad.clave))
                )
                sesion.add_all(
                    TipoIncapacidad(
                        clave=clave, nombre=_nombre_tipo(clave)
                    )
                    for clave in TIPOS_INCAPACIDAD
                    if clave not in existentes
                )
                sesion.commit()
        except SQLAlchemyError as error:
            raise BaseDeDatosError("crear las tablas", error) from error

    def borrar_tablas(self) -> None:
        """Elimina las tablas (y todos sus datos)."""
        try:
            Base.metadata.drop_all(self.engine)
        except SQLAlchemyError as error:
            raise BaseDeDatosError("borrar las tablas", error) from error

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
        Calcula el pago y guarda el caso (INSERT INTO).

        Returns:
            Diccionario con el caso guardado (incluye id y pago).

        Raises:
            IncapacidadError: Si los datos no son válidos (salario,
                días, tipo) o los días no son enteros.
            BaseDeDatosError: Si falla la base de datos.
        """
        pago = calcular_pago_incapacidad(
            salario_mensual=salario,
            dias_incapacidad=dias,
            tipo_incapacidad=tipo_incapacidad,
        )

        if dias != int(dias):
            raise DiasNoEnteros(dias)

        try:
            with Session(self.engine) as sesion:
                tipo = sesion.scalar(
                    select(TipoIncapacidad).where(
                        TipoIncapacidad.clave == tipo_incapacidad
                    )
                )
                caso = CasoIncapacidad(
                    tipo=tipo,
                    salario=salario,
                    dias=int(dias),
                    pago=pago,
                )
                sesion.add(caso)
                sesion.commit()

                return caso.a_diccionario()
        except SQLAlchemyError as error:
            raise BaseDeDatosError("guardar el caso", error) from error

    # ----------------------------------------------------------
    # BUSCAR (SELECT)
    # ----------------------------------------------------------

    def listar_casos(self) -> list[dict]:
        """Retorna todos los casos, del más reciente al más antiguo."""
        return self._consultar(select(CasoIncapacidad))

    def buscar_casos(self, texto: str) -> list[dict]:
        """
        Busca casos cuyo ID, fecha o tipo contengan el texto.

        Raises:
            BusquedaInvalida: Si el texto está vacío o no es texto.
            BaseDeDatosError: Si falla la base de datos.
        """
        if not isinstance(texto, str) or not texto.strip():
            raise BusquedaInvalida()

        texto = texto.strip()

        consulta = (
            select(CasoIncapacidad)
            .join(CasoIncapacidad.tipo)
            .where(
                cast(CasoIncapacidad.id, String).contains(
                    texto, autoescape=True
                )
                | cast(CasoIncapacidad.fecha, String).contains(
                    texto, autoescape=True
                )
                | TipoIncapacidad.nombre.icontains(
                    texto, autoescape=True
                )
                | TipoIncapacidad.clave.icontains(
                    texto, autoescape=True
                )
            )
        )

        return self._consultar(consulta)

    def buscar_caso_por_id(self, id_caso: int) -> dict:
        """
        Busca un caso por su ID exacto.

        Raises:
            CasoNoEncontrado: Si no existe.
            BaseDeDatosError: Si falla la base de datos.
        """
        casos = self._consultar(
            select(CasoIncapacidad).where(
                CasoIncapacidad.id == id_caso
            )
        )

        if not casos:
            raise CasoNoEncontrado(id_caso)

        return casos[0]

    def inicializar_con_fallback(self) -> None:
        """
        Verifica la conexión a la base de datos y aplica fallback a SQLite
        local si no está disponible. Crea las tablas si no existen.

        Esta lógica vive en el Controller (no en la Vista) para respetar
        la regla MVC: solo el Controller se comunica con la base de datos.
        """
        try:
            with self.engine.connect():
                pass
            self.crear_tablas()
        except Exception:
            # Fallback transparente a SQLite local
            engine_sqlite = create_engine(
                f"sqlite:///{RUTA_SQLITE_POR_DEFECTO}"
            )
            self._engine = engine_sqlite
            self.crear_tablas()

    def calcular_caso(
        self,
        salario: float,
        dias: float,
        tipo_incapacidad: str = "enfermedad_general",
    ) -> dict:
        """
        Calcula el pago de una incapacidad sin guardarla en la base de datos.

        Retorna un diccionario con el resultado del cálculo incluyendo
        el porcentaje de reconocimiento, para que la Vista no necesite
        consultar directamente al Modelo.

        Args:
            salario: Salario mensual del empleado.
            dias: Días de incapacidad.
            tipo_incapacidad: Tipo registrado de incapacidad.

        Returns:
            Diccionario con: salario, dias, tipo_incapacidad, porcentaje, pago.

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

    def _consultar(self, consulta) -> list[dict]:
        """Ejecuta un SELECT de casos ordenado por ID descendente."""
        try:
            with Session(self.engine) as sesion:
                casos = sesion.scalars(
                    consulta.order_by(CasoIncapacidad.id.desc())
                )
                return [caso.a_diccionario() for caso in casos]
        except SQLAlchemyError as error:
            raise BaseDeDatosError("consultar los casos", error) from error
