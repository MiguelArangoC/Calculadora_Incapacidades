"""Interfaz de consola: calcular, guardar y buscar incapacidades."""

from src.controller.incapacidad_controller import IncapacidadController
from src.database.conexion import descripcion_conexion
from src.model.incapacidad import IncapacidadError, TIPOS_INCAPACIDAD


class OpcionInvalida(ValueError):
    """Excepción lanzada cuando el usuario ingresa una opción inválida."""


controller = IncapacidadController()


# ============================================================
# ENTRADA Y SALIDA
# ============================================================

def mostrar_menu() -> str:
    print("\n--- Calculadora de Pago por Incapacidad ---")
    print("1. Calcular y guardar incapacidad")
    print("2. Buscar casos guardados")
    print("3. Ver todos los casos")
    print("4. Crear tablas")
    print("5. Borrar tablas")
    print("6. Salir")
    return input("Seleccione una opción: ")


def leer_float(mensaje: str) -> float:
    """Lee un valor desde la consola y lo convierte a float."""
    entrada = input(mensaje)
    return float(entrada)


def leer_datos_incapacidad() -> tuple[float, float]:
    """Lee el salario y los días de incapacidad."""
    salario = leer_float("Ingrese el salario mensual: ")
    dias = leer_float("Ingrese los días de incapacidad: ")
    return salario, dias


def seleccionar_tipo_incapacidad() -> str:
    """Muestra los tipos disponibles y permite al usuario seleccionar uno."""
    print("\nTipos de incapacidad disponibles:")
    tipos_lista = list(TIPOS_INCAPACIDAD.keys())
    for i, tipo in enumerate(tipos_lista, 1):
        print(f"{i}. {tipo}")

    indice_tipo_str = input("Seleccione el tipo de incapacidad (número): ")
    indice_tipo = int(indice_tipo_str) - 1

    if 0 <= indice_tipo < len(tipos_lista):
        return tipos_lista[indice_tipo]
    else:
        raise OpcionInvalida("Opción de tipo de incapacidad inválida.")


def mostrar_casos(casos: list[dict]) -> None:
    """Imprime una lista de casos."""
    if not casos:
        print("\nNo se encontraron casos.")
        return

    print(f"\n{len(casos)} caso(s):")
    for caso in casos:
        print(
            f"  #{caso['id']} | {caso['fecha']} | "
            f"{caso['tipo_nombre']} | {caso['dias']} días | "
            f"Salario ${caso['salario']:,.2f} | "
            f"Pago ${caso['pago']:,.2f}"
        )


# ============================================================
# OPCIONES DEL MENÚ
# ============================================================

def procesar_opcion_calcular() -> None:
    """Calcula la incapacidad, la guarda (INSERT) y muestra el resultado."""
    try:
        salario, dias = leer_datos_incapacidad()
        tipo = seleccionar_tipo_incapacidad()
        caso = controller.insertar_caso(
            salario=salario, dias=dias, tipo_incapacidad=tipo
        )
        print(
            f"\n>> El valor a pagar por incapacidad es: "
            f"${caso['pago']:,.2f} COP (caso guardado #{caso['id']})"
        )
    except OpcionInvalida as e:
        print(f"Error: {e}")
    except ValueError:
        print("Error: Por favor, ingrese valores numéricos válidos para el salario, días y tipo de incapacidad.")
    except IncapacidadError as e:
        print(f"\n{e}")


def procesar_opcion_buscar() -> None:
    """Busca casos por ID, fecha o tipo (SELECT)."""
    try:
        texto = input("Buscar por ID, fecha (AAAA-MM-DD) o tipo: ")
        mostrar_casos(controller.buscar_casos(texto))
    except IncapacidadError as e:
        print(f"\n{e}")


def procesar_opcion_listar() -> None:
    """Muestra todos los casos guardados (SELECT)."""
    try:
        mostrar_casos(controller.listar_casos())
    except IncapacidadError as e:
        print(f"\n{e}")


def procesar_opcion_crear_tablas() -> None:
    """Crea las tablas de la base de datos."""
    try:
        controller.crear_tablas()
        print("\nTablas creadas (o ya existían).")
    except IncapacidadError as e:
        print(f"\n{e}")


def procesar_opcion_borrar_tablas() -> None:
    """Borra las tablas de la base de datos, previa confirmación."""
    confirmacion = input(
        "Se borrarán las tablas y TODOS los casos. Escriba 'si' para continuar: "
    )
    if confirmacion.strip().lower() != "si":
        print("Operación cancelada.")
        return

    try:
        controller.borrar_tablas()
        print("\nTablas borradas.")
    except IncapacidadError as e:
        print(f"\n{e}")


ACCIONES = {
    "1": procesar_opcion_calcular,
    "2": procesar_opcion_buscar,
    "3": procesar_opcion_listar,
    "4": procesar_opcion_crear_tablas,
    "5": procesar_opcion_borrar_tablas,
}


def ejecutar() -> None:
    try:
        print(f"Base de datos: {descripcion_conexion()}")
    except IncapacidadError as e:
        print(e)
        return

    while True:
        opcion = mostrar_menu()
        if opcion in ACCIONES:
            ACCIONES[opcion]()
        elif opcion == "6":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    ejecutar()
