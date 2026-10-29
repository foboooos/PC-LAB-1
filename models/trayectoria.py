"""Modelo básico de una trayectoria peatonal."""

import math
from dataclasses import dataclass, field

from .observacion import Observacion


@dataclass
class Trayectoria:
    """Representa las observaciones y cálculos propios de un peatón."""

    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    def calcular_distancia_total(self) -> float:
        """Suma de las distancias entre posiciones consecutivas."""
        pares = zip(self.observaciones, self.observaciones[1:])
        return sum(math.hypot(b.x - a.x, b.y - a.y) for a, b in pares)

    def calcular_desplazamiento(self) -> float:
        """Distancia en línea recta entre la primera y la última posición."""
        if len(self.observaciones) < 2:
            return 0.0
        inicio, fin = self.observaciones[0], self.observaciones[-1]
        return math.hypot(fin.x - inicio.x, fin.y - inicio.y)

    def calcular_velocidad_media(self, fps: float) -> float:
        """Distancia total dividida por el tiempo total observado (m/s)."""
        if len(self.observaciones) < 2:
            return 0.0
        frames = self.observaciones[-1].frame - self.observaciones[0].frame
        tiempo = frames / fps
        return self.calcular_distancia_total() / tiempo if tiempo > 0 else 0.0

    def calcular_segmentos(
            self, fps: float
        ) -> list[tuple[Observacion, Observacion, float]]:
            """Tramos entre observaciones consecutivas: (inicio, fin, velocidad en m/s)."""
            segmentos = []
            for a, b in zip(self.observaciones, self.observaciones[1:]):
                dt = (b.frame - a.frame) / fps
                if dt > 0:
                    segmentos.append((a, b, math.hypot(b.x - a.x, b.y - a.y) / dt))
            return segmentos
