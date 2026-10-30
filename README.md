# Laboratorio 1 – Análisis de Trayectorias Peatonales

Este proyecto contiene un pipeline en Python que permite procesar nueve experimentos de movimiento peatonal en un corredor, reconstruir trayectorias y calcular indicadores individuales, espaciales y colectivos.

## Requisitos y datos

- Python 3.10 o superior.
- Dependencias de `requirements.txt`: pandas y matplotlib (utilizadas para generar gráficos).

Los datos corresponden al experimento BaSiGo *Pedestrian flow in a unidirectional corridor* ([archivo oficial](https://ped.fz-juelich.de/da/doku.php?id=corridor5), DOI: [10.34735/ped.2013.6](https://doi.org/10.34735/ped.2013.6)). Los archivos `data/uni_corr_500_01.txt` a `uni_corr_500_09.txt` contienen filas con cinco campos:

```text
id frame x/m y/m z/m
```

El pipeline utiliza `x` e `y` en metros; `z` se carga, pero se excluye de los cálculos. La frecuencia se lee de los encabezados de los archivos: 16 FPS en ocho corridas y 25 FPS en la corrida 02, que corresponde a otra vista de cámara. Las corridas 08 y 09 cambian el ancho de salida durante el experimento, por lo que sus promedios mezclan condiciones distintas.

## Estructura

```text
data/        Archivos de entrada (.txt)
models/      Observacion, Trayectoria, Experimento, ResultadoAnalisis
pipeline/    Coordinador, interfaz de etapa y contexto
stages/      Carga, preparación, análisis y exportación
results/     Resultados de ejemplo y figuras generadas
main.py      Punto de entrada del pipeline
graficos.py  Generación de figuras a partir de los CSV
```

## Instalación en Windows (PowerShell)

Ejecuta estos comandos desde la raíz del repositorio:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, permite scripts solo durante esta sesión y vuelve a ejecutar el comando de activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Ejecución en Windows (PowerShell)

```powershell
python main.py --input .\data --output .\results
python graficos.py --results .\results
```

## Instalación en Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Ejecución en Linux

```bash
python3 main.py --input ./data --output ./results
python3 graficos.py --results ./results
```

`main.py` carga los archivos `.txt` directamente dentro de la carpeta indicada, o puede recibir un archivo individual. Si el archivo no se incluyen los FPS en su encabezado, se puede proporcionar con el comando `--fps` luego de `./results`.

| Opción | Descripción | Valor por defecto |
|---|---|---|
| `--input` | Archivo `.txt` o carpeta con archivos `.txt`. | `./data` |
| `--output` | Carpeta con los resultados en formato CSV y JSON. | `./results` |
| `--fps` | FPS de respaldo si el archivo no especifica la frecuencia. | Sin especificar |

## Resultados generados

`main.py` crea la carpeta de salida y escribe los datos tabulares. Luego `graficos.py` lee esos archivos y genera seis imágenes en `figuras/`.

| Archivo | Contenido |
|---|---|
| `individuales.csv` | Indicadores individuales por peatón. |
| `resumen_experimentos.csv` | Métricas agregadas por corrida. |
| `zonas.csv` | Resultados por zona del corredor. |
| `densidad.csv` | Densidad y velocidad por frame. |
| `flujo.csv` | Conteo y flujo en ventanas de 10 segundos. |
| `comparacion.json` | Correlaciones entre promedios de corridas. |
| `figuras/velocidad_vs_densidad.png` | Velocidad media frente a densidad media. |
| `figuras/velocidad_por_zona.png` | Velocidad media en cada zona. |
| `figuras/densidad_tiempo.png` | Evolución temporal de la densidad. |
| `figuras/flujo.png` | Flujo resumen por corrida. |
| `figuras/velocidades_individuales.png` | Distribución de velocidades individuales por corrida. |
| `figuras/flujo_vs_densidad.png` | Flujo medio frente a densidad media. |

## Prueba de extremo a extremo en Linux

El repositorio no cuenta actualmente con un servidor de pruebas automatizadas. El proyecto puede ejecutarse correctamente desde WSL o una máquina virtual, pero no sirve como sustitución de la prueba en el servidor requerido.
