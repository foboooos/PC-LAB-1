"""Etapa de análisis espacial, densidad y flujo."""

from collections import Counter, defaultdict
from statistics import mean

from models.experimento import Experimento
from models.observacion import Observacion
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

N_ZONAS = 5           # el corredor se divide en 5 franjas iguales
VENTANA_FLUJO_S = 10  # el flujo se mide en ventanas de 10 s


def _eje_principal(experimento: Experimento) -> str:
    """El eje con mayor recorrido es el largo del corredor ('x' o 'y')."""
    xs = [o.x for o in experimento.observaciones]
    ys = [o.y for o in experimento.observaciones]
    return "x" if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else "y"


def _principal(o: Observacion, eje: str) -> float:
    return o.x if eje == "x" else o.y


def _area(experimento: Experimento) -> float:
    """Área aproximada del corredor: rectángulo que contiene todas las posiciones."""
    xs = [o.x for o in experimento.observaciones]
    ys = [o.y for o in experimento.observaciones]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa el análisis por zonas y los cálculos de densidad y flujo."""

    def ejecutar(
        self,
        entrada: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las zonas, la densidad y el flujo de cada experimento."""
        for experimento in entrada:
            assert experimento.fps is not None
            fps = experimento.fps
            experimento.resultados_zonas = self._analizar_zonas(experimento)
            experimento.resultados_colectivos.update(self._calcular_densidad(experimento))
            experimento.resultados_colectivos.update(self._calcular_flujo(experimento, fps))
            print(f"  {experimento.nombre}: zonas, densidad y flujo calculados")
        return entrada

    def _analizar_zonas(self, experimento: Experimento) -> dict[str, dict[str, float]]:
        """Peatones, velocidad media y tiempo medio de paso por cada zona."""
        assert experimento.fps is not None
        fps = experimento.fps
        eje = _eje_principal(experimento)
        valores = [_principal(o, eje) for o in experimento.observaciones]
        minimo, maximo = min(valores), max(valores)
        ancho = (maximo - minimo) / N_ZONAS

        def zona_de(o: Observacion) -> int:
            return min(int((_principal(o, eje) - minimo) / ancho), N_ZONAS - 1)

        peatones = defaultdict(set)
        velocidades = defaultdict(list)
        tiempo_en_zona = defaultdict(float)

        for t in experimento.trayectorias:
            for a, b, v in t.calcular_segmentos(fps):
                z = zona_de(a)
                peatones[z].add(t.id_peaton)
                velocidades[z].append(v)
                tiempo_en_zona[(t.id_peaton, z)] += (b.frame - a.frame) / fps

        todas = [v for lista in velocidades.values() for v in lista]
        vel_global = mean(todas) if todas else 0.0

        resultados = {}
        for z in range(N_ZONAS):
            tiempos = [t for (_, zz), t in tiempo_en_zona.items() if zz == z]
            vel_zona = mean(velocidades[z]) if velocidades[z] else 0.0
            resultados[f"zona_{z + 1}"] = {
                "inicio_m": minimo + z * ancho,
                "fin_m": minimo + (z + 1) * ancho,
                "n_peatones": len(peatones[z]),
                "velocidad_media_m_s": vel_zona,
                "tiempo_medio_paso_s": mean(tiempos) if tiempos else 0.0,
                "velocidad_relativa": vel_zona / vel_global if vel_global > 0 else 0.0,
            }
        return resultados

    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        """Densidad ρ = N/A por frame; también guarda la velocidad media de cada frame."""
        assert experimento.fps is not None
        fps = experimento.fps
        area = _area(experimento)
        frame_inicial = min(o.frame for o in experimento.observaciones)

        n_por_frame = Counter(o.frame for o in experimento.observaciones)
        vel_por_frame = defaultdict(list)
        for t in experimento.trayectorias:
            for a, _, v in t.calcular_segmentos(fps):
                vel_por_frame[a.frame].append(v)

        experimento.serie_densidad = [
            {
                "frame": frame,
                "tiempo_s": (frame - frame_inicial) / fps,
                "n_peatones": n,
                "densidad_p_m2": n / area,
                "velocidad_media_m_s": (
                    mean(vel_por_frame[frame]) if vel_por_frame[frame] else float("nan")
                ),
            }
            for frame, n in sorted(n_por_frame.items())
        ]
        densidades = [fila["densidad_p_m2"] for fila in experimento.serie_densidad]
        return {"area_m2": area, "densidad_media_p_m2": mean(densidades)}

    def _calcular_flujo(
        self,
        experimento: Experimento,
        fps: float,
    ) -> dict[str, float]:
        """Flujo J = N/Δt a través de una línea transversal en la mitad del corredor."""
        eje = _eje_principal(experimento)
        valores = [_principal(o, eje) for o in experimento.observaciones]
        linea = (min(valores) + max(valores)) / 2
        frame_inicial = min(o.frame for o in experimento.observaciones)

        cruces = []
        for t in experimento.trayectorias:
            for a, b in zip(t.observaciones, t.observaciones[1:]):
                pa, pb = _principal(a, eje), _principal(b, eje)
                if pa != pb and (pa - linea) * (pb - linea) <= 0:
                    frame = a.frame + (linea - pa) / (pb - pa) * (b.frame - a.frame)
                    cruces.append((frame - frame_inicial) / fps)
                    break
        cruces.sort()

        experimento.serie_flujo = []
        if cruces:
            n_ventanas = int(cruces[-1] // VENTANA_FLUJO_S) + 1
            for k in range(n_ventanas):
                ini, fin = k * VENTANA_FLUJO_S, (k + 1) * VENTANA_FLUJO_S
                n = sum(1 for c in cruces if ini <= c < fin)
                experimento.serie_flujo.append(
                    {"ventana_inicio_s": ini, "ventana_fin_s": fin,
                     "n_cruces": n, "flujo_p_s": n / VENTANA_FLUJO_S}
                )

        duracion = cruces[-1] - cruces[0] if len(cruces) > 1 else 0.0
        return {
            "linea_cruce_m": linea,
            "n_cruces": len(cruces),
            "flujo_p_s": len(cruces) / duracion if duracion > 0 else 0.0,
        }
