"""Genera las figuras del informe a partir de los CSV de results/."""

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

def corto(nombre) -> str:
    """Últimos 2 caracteres del nombre del experimento (ej. '01')."""
    return str(nombre)[-2:]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("./results"))
    ruta = parser.parse_args().results
    figuras = ruta / "figuras"
    figuras.mkdir(exist_ok=True)

    resumen = pd.read_csv(ruta / "resumen_experimentos.csv")
    zonas = pd.read_csv(ruta / "zonas.csv")
    densidad = pd.read_csv(ruta / "densidad.csv")
    indiv = pd.read_csv(ruta / "individuales.csv")

    plt.figure()
    plt.scatter(resumen["densidad_media_p_m2"], resumen["velocidad_media_m_s"])
    for nombre, dens, vel in zip(
        resumen["experimento"].tolist(),
        resumen["densidad_media_p_m2"].tolist(),
        resumen["velocidad_media_m_s"].tolist(),
    ):
        plt.annotate(corto(nombre), (dens, vel))
    plt.xlabel("Densidad media (personas/m²)")
    plt.ylabel("Velocidad media (m/s)")
    plt.title("Velocidad vs densidad por experimento")
    plt.savefig(figuras / "velocidad_vs_densidad.png", dpi=150, bbox_inches="tight")
    plt.close()

    plt.figure()
    for nombre, g in zonas.groupby("experimento"):
        plt.plot(g["zona"], g["velocidad_media_m_s"], marker="o", label=corto(nombre))
    plt.xlabel("Zona del corredor")
    plt.ylabel("Velocidad media (m/s)")
    plt.title("Velocidad por zona")
    plt.legend(title="Experimento")
    plt.savefig(figuras / "velocidad_por_zona.png", dpi=150, bbox_inches="tight")
    plt.close()

    plt.figure()
    for nombre, g in densidad.groupby("experimento"):
        plt.plot(g["tiempo_s"], g["densidad_p_m2"], label=corto(nombre))
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Densidad (personas/m²)")
    plt.title("Densidad en el tiempo")
    plt.legend(title="Experimento")
    plt.savefig(figuras / "densidad_tiempo.png", dpi=150, bbox_inches="tight")
    plt.close()

    plt.figure()
    plt.bar(resumen["experimento"].str[-2:], resumen["flujo_p_s"])
    plt.xlabel("Experimento")
    plt.ylabel("Flujo (personas/s)")
    plt.title("Flujo peatonal por experimento")
    plt.savefig(figuras / "flujo.png", dpi=150, bbox_inches="tight")
    plt.close()

    plt.figure()
    datos = [g["velocidad_media_m_s"] for _, g in indiv.groupby("experimento")]
    etiquetas = [corto(n) for n, _ in indiv.groupby("experimento")]
    plt.boxplot(datos)
    plt.xticks(range(1, len(etiquetas) + 1), etiquetas)
    plt.xlabel("Experimento")
    plt.ylabel("Velocidad media individual (m/s)")
    plt.title("Velocidades individuales")
    plt.savefig(figuras / "velocidades_individuales.png", dpi=150, bbox_inches="tight")
    plt.close()

    plt.figure()
    dens = resumen["densidad_media_p_m2"].tolist()
    flujo = resumen["flujo_p_s"].tolist()
    for nombre, d, j in zip(resumen["experimento"].tolist(), dens, flujo):
        plt.annotate(corto(nombre), (d, j))
    plt.scatter(dens, flujo)
    plt.xlabel("Densidad media (personas/m²)")
    plt.ylabel("Flujo (personas/s)")
    plt.title("Flujo vs densidad")
    plt.savefig(figuras / "flujo_vs_densidad.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Figuras guardadas en {figuras}")


if __name__ == "__main__":
    main()
