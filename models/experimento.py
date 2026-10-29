"""Entidad que agrupa los datos y resultados de un experimento."""

from dataclasses import dataclass, field

from .observacion import Observacion
from .trayectoria import Trayectoria


@dataclass
class Experimento:
    """Representa un conjunto de observaciones y sus análisis."""

    nombre: str
    observaciones: list[Observacion] = field(default_factory=list)
    trayectorias: list[Trayectoria] = field(default_factory=list)
    resultados_individuales: dict[int, dict[str, float]] = field(default_factory=dict)
    resultados_colectivos: dict[str, float] = field(default_factory=dict)
    fps: float | None = None
    resultados_zonas: dict[str, dict[str, float]] = field(default_factory=dict)
    serie_densidad: list[dict[str, float]] = field(default_factory=list)
    serie_flujo: list[dict[str, float]] = field(default_factory=list)
