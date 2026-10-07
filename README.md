# Calculadora de Incapacidades

Aplicación académica en Python para estimar el pago correspondiente a incapacidades laborales en Colombia.

Cuenta con interfaz gráfica (Kivy/KivyMD), interfaz de consola, persistencia con SQLite y generación de ejecutables para Windows y Android.

> **Nota:** Los resultados son una simulación académica y no sustituyen una liquidación oficial realizada por una entidad competente.

---

## Tabla de contenido

- [Tipos de incapacidad](#tipos-de-incapacidad)
- [Proceso de cálculo](#proceso-de-cálculo)
- [Validaciones](#validaciones)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Pruebas](#pruebas)
- [Compilación](#compilación)
- [Alcance y limitaciones](#alcance-y-limitaciones)
- [Integrantes](#integrantes)
- [Licencia](#licencia)

---

## Tipos de incapacidad

| Tipo               | Porcentaje de reconocimiento |
| ------------------ | ---------------------------: |
| Enfermedad general |                       66.67% |
| Maternidad         |                         100% |
| Riesgo laboral     |                         100% |

---

## Proceso de cálculo

Una vez validados los datos:

1. Se identifica el tipo de incapacidad y su porcentaje.
2. Se calcula el valor diario: `salario_mensual / 30`.
3. Se obtiene el pago: `valor_dia × porcentaje × dias_incapacidad`.

### Ejemplo

Salario de $2.500.000, incapacidad de 5 días por enfermedad general:

```
valor_dia = 2.500.000 / 30 = 83.333,33
pago = 83.333,33 × 0.6667 × 5 = 277.778,33
```

---

## Validaciones

Antes de calcular, el programa verifica:

- Salario mayor a cero.
- Días de incapacidad mayores a cero.
- Tipo de incapacidad válido.
- Valores numéricos.
- Datos completos.

Los errores se manejan con excepciones específicas que generan mensajes claros para el usuario.

---

## Estructura del proyecto

```
Calculadora_Incapacidades/
├── main.py                          # Punto de entrada
├── requirements.txt
├── buildozer.spec                   # Configuración Android
│
├── src/
│   ├── database/
│   │   └── database.py              # Persistencia SQLite
│   │
│   ├── model/
│   │   └── incapacidad.py           # Lógica de negocio
│   │
│   └── view/
│       ├── console/
│       │   └── cli.py               # Interfaz de consola
│       └── gui/
│           └── app.py               # Interfaz gráfica (Kivy/KivyMD)
│
├── test/
│   └── test_incapacidad.py
│
└── .github/workflows/
    └── build-windows.yml            # CI para generar el .exe
```

---

## Requisitos

- Python 3.12 (recomendado).
- Git.
- Dependencias listadas en `requirements.txt`.

---

## Instalación

```bash
git clone https://github.com/IRVMakiAkame0/Calculadora_Incapacidades.git
cd Calculadora_Incapacidades

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Ejecución

### Interfaz gráfica

```bash
python main.py
```

### Consola

```bash
python -m src.view.console.cli
```

---

## Pruebas

```bash
python -m pytest
```

O con `unittest`:

```bash
python -m unittest discover -s test -v
```

---

## Compilación

### Windows

El workflow de GitHub Actions (`.github/workflows/build-windows.yml`) ejecuta las pruebas y genera el ejecutable con PyInstaller. El artefacto resultante se publica como `CalculadoraIncapacidades-Windows`.

Para generar el ejecutable manualmente:

```bash
python -m PyInstaller --noconfirm --clean --onedir --windowed \
    --name CalculadoraIncapacidades --paths . src/view/gui/app.py
```

### Android

La configuración se encuentra en `buildozer.spec`. Para generar el APK en un entorno compatible:

```bash
buildozer android debug
```

---

## Alcance y limitaciones

- Los porcentajes y reglas corresponden a la lógica académica del proyecto.
- No se contemplan todos los escenarios administrativos de una liquidación real.
- Los resultados no deben interpretarse como asesoría legal o laboral.

---

## Integrantes

### Desarrollo base

Lógica inicial del proyecto suministrada por el docente:

- Miguel Ángel Arango Cardona
- Juan Camilo García Castro

### Desarrollo y ampliación

| Integrante              | GitHub                                             |
| ----------------------- | -------------------------------------------------- |
| Isabella Ruiz Velasquez | [@IRVMakiAkame0](https://github.com/IRVMakiAkame0) |
| Andrés Rosas            | [@andres-rosas](https://github.com/andres-rosas)   |

---

## Licencia

Proyecto desarrollado con fines académicos para la aplicación de principios de Clean Code y buenas prácticas de desarrollo de software.
