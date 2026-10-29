"""Etapa de comparación de experimentos."""

from statistics import StatisticsError, correlation, mean

from models.experimento import Experimento
from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


def _correlacion(xs: list[float], ys: list[float]) -> float:
    """Correlación de Pearson; devuelve NaN si no se puede calcular."""
    try:
        return correlation(xs, ys)
    except (StatisticsError, ValueError):
        return float("nan")


class ComparacionExperimentos(
    EtapaPipeline[list[Experimento], ResultadoAnalisis]
):
    """Compara resultados de varios experimentos."""

    def ejecutar(
        self,
        entrada: list[Experimento],
        contexto: ContextoPipeline,
    ) -> ResultadoAnalisis:
        """Retorna los experimentos junto con sus resultados comparativos."""
        for experimento in entrada:
            self._resumir(experimento)
        comparacion = self._comparar(entrada)
        print(f"  {len(entrada)} experimentos comparados")
        return ResultadoAnalisis(experimentos=entrada, comparacion=comparacion)

    def _resumir(self, experimento: Experimento) -> None:
        """Agrega al experimento su resumen (lo que pide la sección 5.7)."""
        individuales = list(experimento.resultados_individuales.values())
        def promedio(clave: str) -> float:
            return mean(r[clave] for r in individuales)

        filas = [
            f for f in experimento.serie_densidad
            if f["velocidad_media_m_s"] == f["velocidad_media_m_s"]
        ]
        experimento.resultados_colectivos.update({
            "n_peatones": len(individuales),
            "velocidad_media_m_s": promedio("velocidad_media_m_s"),
            "distancia_media_m": promedio("distancia_total_m"),
            "tiempo_medio_s": promedio("tiempo_total_s"),
            "eficiencia_media": promedio("eficiencia"),
            "porcentaje_detenido_medio": promedio("porcentaje_detenido"),
            "correlacion_densidad_velocidad_frames": _correlacion(
                [f["densidad_p_m2"] for f in filas],
                [f["velocidad_media_m_s"] for f in filas],
            ),
        })

    def _comparar(self, experimentos: list[Experimento]) -> dict[str, float]:
        """Relaciones entre experimentos (densidad, velocidad y flujo)."""
        densidades = [e.resultados_colectivos["densidad_media_p_m2"] for e in experimentos]
        velocidades = [e.resultados_colectivos["velocidad_media_m_s"] for e in experimentos]
        flujos = [e.resultados_colectivos["flujo_p_s"] for e in experimentos]
        return {
            "n_experimentos": len(experimentos),
            "correlacion_densidad_velocidad": _correlacion(densidades, velocidades),
            "correlacion_densidad_flujo": _correlacion(densidades, flujos),
        }
