"""Etapa de exportación de resultados."""

import csv
import json
from pathlib import Path

from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


def _escribir_csv(ruta: Path, filas: list[dict]) -> None:
    """Escribe una lista de diccionarios como CSV (columnas = claves de la primera fila)."""
    if not filas:
        return
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


class ExportacionResultados(EtapaPipeline[ResultadoAnalisis, None]):
    """Exporta los resultados de los experimentos y su comparación."""

    def ejecutar(
        self,
        entrada: ResultadoAnalisis,
        contexto: ContextoPipeline,
    ) -> None:
        """Guarda los resultados en la ruta de salida configurada."""
        contexto.ruta_salida.mkdir(parents=True, exist_ok=True)
        self._exportar(entrada, contexto.ruta_salida)
        print(f"  Resultados guardados en {contexto.ruta_salida}")

    def _exportar(self, resultados: ResultadoAnalisis, ruta_salida: Path) -> None:
        """Exporta los resultados a la ruta indicada."""
        exps = resultados.experimentos

        individuales = [
            {"experimento": e.nombre, "id_peaton": id_peaton, **r}
            for e in exps
            for id_peaton, r in e.resultados_individuales.items()
        ]
        resumen = [{"experimento": e.nombre, **e.resultados_colectivos} for e in exps]
        zonas = [
            {"experimento": e.nombre, "zona": zona, **datos}
            for e in exps
            for zona, datos in e.resultados_zonas.items()
        ]
        densidad = [{"experimento": e.nombre, **f} for e in exps for f in e.serie_densidad]
        flujo = [{"experimento": e.nombre, **f} for e in exps for f in e.serie_flujo]

        _escribir_csv(ruta_salida / "individuales.csv", individuales)
        _escribir_csv(ruta_salida / "resumen_experimentos.csv", resumen)
        _escribir_csv(ruta_salida / "zonas.csv", zonas)
        _escribir_csv(ruta_salida / "densidad.csv", densidad)
        _escribir_csv(ruta_salida / "flujo.csv", flujo)
        with open(ruta_salida / "comparacion.json", "w", encoding="utf-8") as archivo:
            json.dump(resultados.comparacion, archivo, indent=2)
