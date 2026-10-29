"""Etapa de análisis individual de los experimentos."""

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

# Criterio de detención:
# un peatón está detenido si su velocidad es menor a 0,1 m/s
# durante al menos 0,5 s seguidos.
UMBRAL_VELOCIDAD = 0.1   # m/s
DURACION_MINIMA = 0.5    # s


class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Coordina el análisis de múltiples trayectorias y reúne sus indicadores."""

    def ejecutar(
        self,
        entrada: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las trayectorias de cada experimento."""
        for experimento in entrada:
            fps = experimento.fps
            if fps is None:
                raise ValueError(
                    f"{experimento.nombre}: no se conoce el fps. Usa --fps."
                )
            resultados = {
                t.id_peaton: self._calcular_indicadores(t, fps)
                for t in experimento.trayectorias
            }
            experimento.resultados_individuales = {
                id_peaton: r for id_peaton, r in resultados.items() if r
            }
            print(
                f"  {experimento.nombre}: "
                f"{len(experimento.resultados_individuales)} peatones analizados"
            )
        return entrada

    def _calcular_indicadores(
        self,
        trayectoria: Trayectoria,
        fps: float,
    ) -> dict[str, float]:
        """Calcula los indicadores individuales de una trayectoria."""
        obs = trayectoria.observaciones
        if len(obs) < 2:
            return {}

        segmentos = trayectoria.calcular_segmentos(fps)
        velocidades = [v for _, _, v in segmentos]
        distancia = trayectoria.calcular_distancia_total()
        desplazamiento = trayectoria.calcular_desplazamiento()
        tiempo_total = (obs[-1].frame - obs[0].frame) / fps

        detenciones = self._detectar_detenciones(trayectoria, fps)
        tiempo_detenido = sum((fin - ini) / fps for ini, fin in detenciones)

        return {
            "x_inicial": obs[0].x,
            "y_inicial": obs[0].y,
            "x_final": obs[-1].x,
            "y_final": obs[-1].y,
            "tiempo_total_s": tiempo_total,
            "distancia_total_m": distancia,
            "desplazamiento_m": desplazamiento,
            "velocidad_media_m_s": trayectoria.calcular_velocidad_media(fps),
            "velocidad_maxima_m_s": max(velocidades) if velocidades else 0.0,
            "eficiencia": desplazamiento / distancia if distancia > 0 else 0.0,
            "n_detenciones": len(detenciones),
            "tiempo_detenido_s": tiempo_detenido,
            "porcentaje_detenido": (
                100 * tiempo_detenido / tiempo_total if tiempo_total > 0 else 0.0
            ),
        }

    def _detectar_detenciones(
        self,
        trayectoria: Trayectoria,
        fps: float,
    ) -> list[tuple[int, int]]:
        """Identifica intervalos (frame_inicio, frame_fin) de detención."""
        intervalos = []
        inicio = fin = None
        for a, b, v in trayectoria.calcular_segmentos(fps):
            if v < UMBRAL_VELOCIDAD:
                if inicio is None:
                    inicio = a.frame
                fin = b.frame
            elif inicio is not None:
                intervalos.append((inicio, fin))
                inicio = None
        if inicio is not None:
            intervalos.append((inicio, fin))

        return list(filter(lambda i: (i[1] - i[0]) / fps >= DURACION_MINIMA, intervalos))
