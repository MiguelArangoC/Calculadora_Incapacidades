from src.model.incapacidad import calcular_pago_incapacidad, TIPOS_INCAPACIDAD, IncapacidadError

def mostrar_menu() -> str:
    print("\n--- Calculadora de Pago por Incapacidad ---")
    print("1. Calcular incapacidad")
    print("2. Salir")
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
        raise ValueError("Opción de tipo de incapacidad inválida.")

def procesar_calculo(salario: float, dias: float, tipo_seleccionado: str) -> None:
    """Realiza el cálculo de la incapacidad e imprime el resultado."""
    pago = calcular_pago_incapacidad(salario_mensual=salario, dias_incapacidad=dias, tipo_incapacidad=tipo_seleccionado)
    print(f"\n>> El valor a pagar por incapacidad es: ${pago:,.2f} COP")

def procesar_opcion_calcular() -> None:
    """Maneja el flujo principal de cálculo y sus posibles excepciones."""
    try:
        salario, dias = leer_datos_incapacidad()
        tipo_seleccionado = seleccionar_tipo_incapacidad()
        procesar_calculo(salario, dias, tipo_seleccionado)
    except ValueError as e:
        if str(e) == "Opción de tipo de incapacidad inválida.":
            print("Error: Opción de tipo de incapacidad inválida.")
        else:
            print("Error: Por favor, ingrese valores numéricos válidos para el salario, días y tipo de incapacidad.")
    except IncapacidadError as e:
        print(f"\n{e}")

def ejecutar() -> None:
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            procesar_opcion_calcular()
        elif opcion == "2":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    ejecutar()
