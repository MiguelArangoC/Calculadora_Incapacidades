from src.model.incapacidad import *

def mostrar_menu() -> str:
    print("\n--- Calculadora de Pago por Incapacidad ---")
    print("1. Calcular incapacidad")
    print("2. Salir")
    return input("Seleccione una opción: ")

def ejecutar() -> None:
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            try:
                salario_input = input("Ingrese el salario mensual: ")
                salario = float(salario_input)
                
                dias_input = input("Ingrese los días de incapacidad: ")
                dias = float(dias_input)
                
                print("\nTipos de incapacidad disponibles:")
                tipos_lista = list(TIPOS_INCAPACIDAD.keys())
                for i, tipo in enumerate(tipos_lista, 1):
                    print(f"{i}. {tipo}")
                
                tipo_idx_str = input("Seleccione el tipo de incapacidad (número): ")
                tipo_idx = int(tipo_idx_str) - 1
                
                if 0 <= tipo_idx < len(tipos_lista):
                    tipo_seleccionado = tipos_lista[tipo_idx]
                else:
                    print("Error: Opción de tipo de incapacidad inválida.")
                    continue
                
                pago = calcular_pago_incapacidad(salario, dias, tipo_seleccionado)
                print(f"\n>> El valor a pagar por incapacidad es: ${pago:,.2f} COP")
                
            except ValueError:
                print("Error: Por favor, ingrese valores numéricos válidos para el salario, días y tipo de incapacidad.")
            except (SalarioInvalido, DiasIncapacidadInvalidos, TipoIncapacidadInvalido) as e:
                print(f"\n{e}")
            except Exception as e:
                print(f"\nError inesperado: {e}")
        
        elif opcion == "2":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    ejecutar()
