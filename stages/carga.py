"""Etapa de carga de varios experimentos."""

from pathlib import Path

from models.experimento import Experimento
from models.observacion import Observacion
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):
    """Carga una colección de experimentos desde la ruta configurada."""

    def ejecutar(
        self,
        entrada: None,
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Carga los experimentos indicados por la configuración."""
        experimentos = self._cargar_experimentos(contexto.ruta_entrada)


        for experimento in experimentos:
            if experimento.fps is None:
                experimento.fps = contexto.fps

        print(f"  Experimentos cargados: {len(experimentos)}")
        return experimentos

    def _cargar_experimentos(self, ruta_entrada: Path) -> list[Experimento]:
        """Carga los experimentos disponibles en la ruta recibida."""
        if ruta_entrada.is_dir():
            archivos = sorted(ruta_entrada.glob("*.txt"))
        else:
            archivos = [ruta_entrada]
        return [self._leer_archivo(archivo) for archivo in archivos]

    def _leer_archivo(self, ruta: Path) -> Experimento:
        """Lee un archivo de datos y lo convierte en un Experimento."""
        observaciones = []
        fps = None

        with open(ruta, encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue


                if linea.startswith("#"):
                    if "framerate" in linea:
                        fps = float(linea.split(":")[1].split()[0])
                    continue


                partes = linea.split()
                if len(partes) != 5:
                    continue
                try:
                    observaciones.append(
                        Observacion(
                            int(partes[0]),
                            int(partes[1]),
                            float(partes[2]),
                            float(partes[3]),
                            float(partes[4]),
                        )
                    )
                except ValueError:
                    continue

        return Experimento(nombre=ruta.stem, observaciones=observaciones, fps=fps)
