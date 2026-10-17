"""
Pruebas del Controller con base de datos (ORM).

Las pruebas usan una base SQLite en memoria, así que no necesitan
servidor ni ``secret_config.py``.

Fixtures (clase ``BaseDatosTestCase``):
    setUp    -> crea el engine en memoria y las tablas
    tearDown -> borra las tablas y cierra el engine

Ejecutar con:

    python -m unittest discover -s test -v
"""

import unittest

from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from src.controller.incapacidad_controller import (
    BaseDeDatosError,
    BusquedaInvalida,
    CasoNoEncontrado,
    DiasNoEnteros,
    IncapacidadController,
)
from src.model.incapacidad import (
    DiasIncapacidadInvalidos,
    SalarioInvalido,
    TipoIncapacidadInvalido,
)


def crear_engine_en_memoria():
    """Crea una base SQLite en memoria compartida por conexiones."""
    return create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


class BaseDatosTestCase(unittest.TestCase):
    """Fixture: cada prueba arranca con tablas nuevas y vacías."""

    def setUp(self):
        self.engine = crear_engine_en_memoria()
        self.controller = IncapacidadController(self.engine)
        self.controller.crear_tablas()

    def tearDown(self):
        self.controller.borrar_tablas()
        self.engine.dispose()


class TestCrearYBorrarTablas(BaseDatosTestCase):
    """Crear y borrar tablas."""

    def test_crear_tablas_crea_ambas_tablas(self):
        """Normal: las tablas existen después de crearlas."""
        tablas = inspect(self.engine).get_table_names()

        self.assertIn("tipos_incapacidad", tablas)
        self.assertIn("casos_incapacidad", tablas)

    def test_crear_tablas_dos_veces_no_duplica_tipos(self):
        """Normal: crear de nuevo conserva el catálogo sin duplicar."""
        self.controller.crear_tablas()
        self.controller.insertar_caso(2_000_000, 1)

        self.assertEqual(len(self.controller.listar_casos()), 1)

    def test_borrar_tablas_las_elimina(self):
        """Normal: tras borrar no queda ninguna tabla."""
        self.controller.borrar_tablas()

        self.assertEqual(inspect(self.engine).get_table_names(), [])

    def test_crear_tablas_con_conexion_invalida_falla(self):
        """Error: una ruta inexistente produce BaseDeDatosError."""
        engine = create_engine("sqlite:////ruta/que/no/existe/x.db")
        controller = IncapacidadController(engine)

        with self.assertRaises(BaseDeDatosError):
            controller.crear_tablas()

    def test_borrar_tablas_con_conexion_invalida_falla(self):
        """Error: borrar con conexión inválida produce BaseDeDatosError."""
        engine = create_engine("sqlite:////ruta/que/no/existe/x.db")
        controller = IncapacidadController(engine)

        with self.assertRaises(BaseDeDatosError):
            controller.borrar_tablas()


class TestInsertar(BaseDatosTestCase):
    """Insertar casos (INSERT INTO)."""

    def test_insertar_caso_retorna_id_y_pago(self):
        """Normal: guarda el caso y calcula el pago correcto."""
        caso = self.controller.insertar_caso(
            salario=2_500_000,
            dias=10,
            tipo_incapacidad="enfermedad_general",
        )

        self.assertEqual(caso["id"], 1)
        self.assertEqual(caso["tipo_nombre"], "Enfermedad General")
        self.assertAlmostEqual(caso["pago"], 555_583.3333, places=3)

    def test_insertar_maternidad_paga_100_por_ciento(self):
        """Normal: maternidad reconoce el 100 % del salario diario."""
        caso = self.controller.insertar_caso(
            salario=3_000_000,
            dias=5,
            tipo_incapacidad="maternidad",
        )

        self.assertAlmostEqual(caso["pago"], 500_000.0)

    def test_insertar_varios_casos_asigna_ids_consecutivos(self):
        """Normal: cada inserción recibe un ID nuevo."""
        primero = self.controller.insertar_caso(2_000_000, 1)
        segundo = self.controller.insertar_caso(2_000_000, 2)

        self.assertEqual((primero["id"], segundo["id"]), (1, 2))

    def test_insertar_salario_invalido_falla_y_no_guarda(self):
        """Error: salario cero se rechaza y no queda registro."""
        with self.assertRaises(SalarioInvalido):
            self.controller.insertar_caso(salario=0, dias=5)

        self.assertEqual(self.controller.listar_casos(), [])

    def test_insertar_dias_invalidos_falla(self):
        """Error: días negativos se rechazan."""
        with self.assertRaises(DiasIncapacidadInvalidos):
            self.controller.insertar_caso(salario=2_000_000, dias=-3)

    def test_insertar_tipo_invalido_falla(self):
        """Error: un tipo no registrado se rechaza."""
        with self.assertRaises(TipoIncapacidadInvalido):
            self.controller.insertar_caso(
                salario=2_000_000, dias=3, tipo_incapacidad="otro"
            )

    def test_insertar_dias_decimales_falla(self):
        """Error: los días deben ser enteros para guardarse."""
        with self.assertRaises(DiasNoEnteros):
            self.controller.insertar_caso(salario=2_000_000, dias=2.5)

    def test_insertar_sin_tablas_falla(self):
        """Error: sin tablas creadas se lanza BaseDeDatosError."""
        self.controller.borrar_tablas()

        with self.assertRaises(BaseDeDatosError):
            self.controller.insertar_caso(salario=2_000_000, dias=3)


class TestBuscar(BaseDatosTestCase):
    """Consultar casos (SELECT)."""

    def setUp(self):
        super().setUp()
        self.controller.insertar_caso(2_000_000, 3, "enfermedad_general")
        self.controller.insertar_caso(3_000_000, 90, "maternidad")
        self.controller.insertar_caso(1_800_000, 7, "riesgo_laboral")

    def test_listar_casos_ordena_del_mas_reciente(self):
        """Normal: lista todos con el último ID primero."""
        ids = [caso["id"] for caso in self.controller.listar_casos()]

        self.assertEqual(ids, [3, 2, 1])

    def test_buscar_por_nombre_de_tipo_sin_importar_mayusculas(self):
        """Normal: 'MATERNIDAD' encuentra el caso de maternidad."""
        casos = self.controller.buscar_casos("MATERNIDAD")

        self.assertEqual([caso["id"] for caso in casos], [2])

    def test_buscar_por_clave_con_guion_bajo(self):
        """Normal: 'riesgo_laboral' encuentra el caso por su clave."""
        casos = self.controller.buscar_casos("riesgo_laboral")

        self.assertEqual([caso["id"] for caso in casos], [3])

    def test_buscar_por_id(self):
        """Normal: buscar por ID exacto retorna ese caso."""
        caso = self.controller.buscar_caso_por_id(1)

        self.assertEqual(caso["tipo_incapacidad"], "enfermedad_general")

    def test_buscar_por_fecha_del_dia(self):
        """Normal: buscar por el año actual encuentra los tres casos."""
        anio = self.controller.listar_casos()[0]["fecha"][:4]

        self.assertEqual(len(self.controller.buscar_casos(anio)), 3)

    def test_buscar_sin_coincidencias_retorna_lista_vacia(self):
        """Normal: un texto sin resultados no es un error."""
        self.assertEqual(self.controller.buscar_casos("zzz"), [])

    def test_buscar_texto_vacio_falla(self):
        """Error: el texto en blanco se rechaza."""
        with self.assertRaises(BusquedaInvalida):
            self.controller.buscar_casos("   ")

    def test_buscar_id_inexistente_falla(self):
        """Error: un ID que no existe lanza CasoNoEncontrado."""
        with self.assertRaises(CasoNoEncontrado):
            self.controller.buscar_caso_por_id(999)

    def test_buscar_sin_tablas_falla(self):
        """Error: sin tablas se lanza BaseDeDatosError."""
        self.controller.borrar_tablas()

        with self.assertRaises(BaseDeDatosError):
            self.controller.buscar_casos("maternidad")


if __name__ == "__main__":
    unittest.main()
