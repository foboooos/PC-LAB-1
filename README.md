# Laboratorio 1 – Análisis de Trayectorias Peatonales

Pipeline en Python que carga datos de experimentos de movimiento peatonal
(corredor unidireccional), reconstruye trayectorias y calcula indicadores
individuales, por zonas, de densidad y de flujo.

## Requisitos

- Python 3.10 o superior
- Linux (probado también en Windows)

```bash
pip install -r requirements.txt
```

## Estructura

```
data/        archivos de entrada (uni_corr_500_01.txt ... 09.txt)
models/      clases: Observacion, Trayectoria, Experimento, ResultadoAnalisis
pipeline/    infraestructura del pipeline (Pipeline, EtapaPipeline, contexto)
stages/      etapas: carga, preparacion, individual, espacial, colectivo, exportacion
results/     archivos generados
main.py      punto de entrada
graficos.py  genera las figuras del informe
```

## Ejecución

```bash
python3 main.py --input ./data --output ./results
python3 graficos.py --results ./results
```

Parámetros de `main.py`:

- `--input`: archivo o carpeta con los datos (por defecto `data`).
- `--output`: carpeta de resultados (por defecto `results`).
- `--fps`: frecuencia de muestreo.

## Resultados generados (carpeta `results/`)

| Archivo | Contenido |
|---|---|
| `individuales.csv` | indicadores por peatón |
| `resumen_experimentos.csv` | resumen por experimento |
| `zonas.csv` | análisis por zonas |
| `densidad.csv` | densidad y velocidad en el tiempo |
| `flujo.csv` | flujo por ventanas de 10 s |
| `comparacion.json` | correlaciones entre experimentos |
| `figuras/` | gráficos para el informe |

## Decisiones principales

- Se descartan observaciones con frame 0, coordenadas inválidas o frames repetidos.
- Detención: velocidad < 0,1 m/s durante al menos 0,5 s seguidos.
- Zonas: el corredor se divide en 5 franjas iguales a lo largo de su eje mayor.
- Densidad: personas presentes / área (rectángulo que contiene las posiciones).
- Flujo: cruces de una línea transversal en la mitad del corredor.
