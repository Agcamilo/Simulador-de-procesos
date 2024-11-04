from typing import List

from tabulate import tabulate

from Proceso import Proceso, Estado



class CargaTrabajo:
    """Representa un conjunto de Procesos a ejecutar."""
    headers = ["PID", "TA", "TI", "Mem (kB)", "Estado", "Progreso (%)"]

    def terminada(self):
        """Retorna `True` si todos los procesos de la carga de trabajo están en TERMINADO o DENEGADO."""
        return all(p.estado == Estado.TERMINADO or p.estado == Estado.DENEGADO for p in self.procesos)

    def __init__(self, archivo: str):
        """Inicializa una CargaTrabajo a partir de un archivo CSV."""
        self.procesos: List[Proceso] = []
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f.readlines():
                [pid, ta, ti, mem] = linea.split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), int(mem)*1024))
        self.procesos.sort(key=lambda p: p.t_arribo)

    def __repr__(self):
    #Muestra la CargaTrabajo en un formato más simple con clave:valor.
        resultado = ""
        for p in self.procesos:
            resultado += (
                f"PID: {p.id}\n"
                f"TA: {p.t_arribo}\n"
                f"TI: {p.t_irrup}\n"
                f"Mem (kB): {(p.memoria)*1024}\n"
                f"Estado: {p.estado}\n"
                f"Progreso (%): {progreso(p.porcentaje_progreso())}\n"
                "-------------------------\n"
            )
        return resultado


def progreso(porcentaje: float) -> str:
    """Muestra el progreso de un `Proceso` mediante una barra de progeso."""
    cantidad = int((15 * porcentaje / 100))
    return f"{'█' * cantidad}{'_' * (15 - cantidad)} {round(porcentaje, 1)}"
