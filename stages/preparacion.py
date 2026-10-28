"""Etapa de preparación de observaciones y trayectorias."""

import math

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa validación, organización y reconstrucción de trayectorias."""

    def ejecutar(
        self,
        entrada: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Prepara las observaciones y trayectorias de cada experimento."""
        for experimento in entrada:
            total = len(experimento.observaciones)
            validas = self._validar_observaciones(experimento.observaciones)
            organizadas = self._organizar_observaciones(validas)

            experimento.observaciones = validas
            experimento.trayectorias = self._reconstruir_trayectorias(organizadas)

            print(
                f"  {experimento.nombre}: {len(validas)}/{total} observaciones válidas, "
                f"{len(experimento.trayectorias)} peatones"
            )
        return entrada

    def _validar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> list[Observacion]:
        """Quita observaciones con x o y inválidos y frames repetidos."""

        con_numeros = filter(
            lambda o: math.isfinite(o.x) and math.isfinite(o.y), observaciones
        )
        vistos = set()
        validas = []
        for o in con_numeros:
            clave = (o.id_peaton, o.frame)
            if clave not in vistos:
                vistos.add(clave)
                validas.append(o)
        return validas

    def _organizar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> dict[int, list[Observacion]]:
        """Agrupa por peatón y ordena cada grupo por frame."""
        grupos: dict[int, list[Observacion]] = {}
        for o in observaciones:
            grupos.setdefault(o.id_peaton, []).append(o)
        return {
            id_peaton: sorted(lista, key=lambda o: o.frame)
            for id_peaton, lista in sorted(grupos.items())
        }

    def _reconstruir_trayectorias(
        self,
        observaciones_organizadas: dict[int, list[Observacion]],
    ) -> list[Trayectoria]:
        """Crea una Trayectoria por cada peatón."""
        return [
            Trayectoria(id_peaton, lista)
            for id_peaton, lista in observaciones_organizadas.items()
        ]
