from typing import List

from tabulate import tabulate

from Proceso import Proceso

from Proceso import d1

class CargaTrabajo:
    """Representa un conjunto de Procesos a ejecutar."""
    headers = ["PID", "TA", "TI", "Mem (kB)", "Estado", "Progreso (%)"]

    def terminada(self):
        """Retorna `True` si todos los procesos de la carga de trabajo están en TERMINADO o INCORRETO."""
        return all(p.estado == d1["TERMINADO"] or p.estado == d1["INCORRECTO"] for p in self.procesos)

    def __init__(self, archivo: str):
        """Inicializa una CargaTrabajo a partir de un archivo CSV."""
        # Verifica que el archivo tenga la extensión .csv
        if not archivo.lower().endswith('.csv'):
            raise ValueError("El archivo debe tener la extensión .csv")

        self.procesos: List[Proceso] = []
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f.readlines():
                [pid, ta, ti, mem] = linea.strip().split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), int(mem) * 1024))
        self.procesos.sort(key=lambda p: p.tiempo_arribo)

    def __repr__(self):
    #Muestra la CargaTrabajo en un formato más simple con clave:valor.
        resultado = ""
        for p in self.procesos:
            resultado += (
                f"PID: {p.id}\n"
                f"TA: {p.tiempo_arribo}\n"
                f"TI: {p.tiempo_irrupcion}\n"
                f"Mem (kB): {(p.memoria)*1024}\n"
                f"Estado: {p.estado}\n"
                f"Progreso (%): {progreso(p.mostrar_progreso())}\n"
                "-------------------------\n"
            )
        return resultado


def progreso(porcentaje: float) -> str:
    """Muestra el progreso de un `Proceso` mediante una barra de progeso."""
    cantidad = int((15 * porcentaje / 100))
    return f"{'█' * cantidad}{'_' * (15 - cantidad)} {round(porcentaje, 1)}"
