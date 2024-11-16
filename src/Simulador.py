from typing import Optional, List
from tabulate import tabulate
from Particion import Particion
from Proceso import Proceso, d1
from CargarProcesos import CargaTrabajo

def kb_a_bytes(kilobytes: int) -> int:
    return kilobytes * 1024

class Simulador:
    """Representa la simulación."""

    def __init__(self, carga: CargaTrabajo):
        self.carga = carga
        self.cola_listos: List[Proceso] = []
        self.cola_listos_suspendidos: List[Proceso] = []
        self.ejecutando: Optional[Proceso] = None

        # Datos para la memoria
        p0 = Particion(0, kb_a_bytes(100))
        p1 = Particion(p0.dir_inicio + p0.memoria, kb_a_bytes(250))
        p2 = Particion(p1.dir_inicio + p1.memoria, kb_a_bytes(150))
        p3 = Particion(p2.dir_inicio + p2.memoria, kb_a_bytes(50))
        self.memoria_principal: List[Particion] = [p1, p2, p3]
    
        self.max_multiprogramacion: int = 5

        self.t: int = 0
        self.quantum: int = 0

    def terminados(self) -> bool:
        return self.carga.terminada()

    def grado_multiprogramacion(self) -> int:
        # Retorna la cantidad de procesos alojados en memoria principal y virtual
        ejecutando = 1 if self.ejecutando else 0
        return ejecutando + len(self.cola_listos) + len(self.cola_listos_suspendidos)


    def procesos_nuevos(self) -> List[Proceso]:
        # Retorna una lista con los procesos que llegan en el tiempo actual
        return list(filter(lambda p: p.tiempo_arribo <= self.t and p.estado == d1["NUEVO"], self.carga.procesos))


    def encontrar_particion_libre(self, proceso: Proceso) -> Optional[Particion]:
        # Retorna una partición de memoria libre para el proceso según el algoritmo worst-fit.
        peor_part: Optional[Particion] = None
        for part in self.memoria_principal:
            if part.proceso is None and part.memoria >= proceso.memoria:
                if peor_part is None or part.memoria > peor_part.memoria:
                    peor_part = part
        return peor_part

    def encontrar_particion_proceso(self, proceso: Proceso) -> Optional[Particion]:
        # Retorna la partición que está asignada al proceso pasado por parámetro.
        for part in self.memoria_principal :
            if part.proceso == proceso:
                return part

    def cambiar_cola(self, part: Particion):
        # Cambia el proceso de la cola de listos suspendidos a la cola de listos.
        proceso = part.proceso
        if proceso.estado == d1["LYS"]:
            proceso.estado = d1["LISTO"]
            self.cola_listos.append(proceso)
            self.cola_listos_suspendidos.remove(proceso)

    def admitir_proceso(self, proceso: Proceso):
        # Asigna una partición de memoria (en MP o MV) al proceso, o lo rechaza si no hay disponibles.
        part = self.encontrar_particion_libre(proceso)
        if part and part.presente:
            part.proceso = proceso
            proceso.estado = d1["LISTO"]
            self.cola_listos.append(proceso)
            return

        if self.grado_multiprogramacion() < self.max_multiprogramacion:
            # Si no hay espacio en memoria principal, intenta agregarlo a la lista de listos suspendidos
            proceso.estado = d1["LYS"]
            self.cola_listos_suspendidos.append(proceso)
            
            #if part_ocupada is None:
            #    # El proceso no entra en ninguna particion, se lo denega para siempre
            #    print(f"Proceso {proceso.id} no entra en ninguna particion")
            #    proceso.estado = d1["INCORRECTO"]
            #    return
        else:
            # Rechazar proceso, volvera a internar en el siguiente instante de tiempo
            print(f"Proceso {proceso.id} rechazado por falta de espacio")

    def terminar_procesos(self):
        # Verifica que hay un proceso en ejecución
        if self.ejecutando is None:
            print("No hay proceso en ejecución.")
            return
        # Termina el proceso en ejecución en la CPU y libera su partición de memoria asignada.
        part = self.encontrar_particion_proceso(self.ejecutando)
        if part is not None:  # Asegúrate de que `part` no sea None
            part.proceso = None
        self.ejecutando.estado = d1["TERMINADO"]
        self.ejecutando = None
        self.quantum = 0

    def expropiar_proceso(self):
        # Expropia el proceso en ejecución en la CPU y lo manda a la cola de listos.
        self.cola_listos.append(self.ejecutando)
        self.ejecutando.estado = d1["LISTO"]
        self.ejecutando = None

    def activar_proceso(self, proceso: Proceso):
        # Activa un proceso en la CPU y lo asigna a una partición de memoria.
        part = self.encontrar_particion_proceso(proceso)
        if part is None:
            # Proceso estaba suspendido sin partición asignada, se le asigna una.
            part = self.encontrar_particion_libre(proceso)
            if part and part.presente:
                # Se le asigna una.
                part.proceso = proceso
                proceso.estado = d1["LISTO"]
                return
            
        if not part.presente:
            # Proceso estaba suspendido, se lo trae a MP.
            self.cambiar_cola(part)

    def asignar_cpu(self):
        # Asigna la CPU al siguiente proceso de la cola de listos, y lo activa si está en mem virtual.
        if 0 == len(self.cola_listos):
            self.ejecutando = None
        else:
            self.ejecutando = self.cola_listos[0]
            self.activar_proceso(self.ejecutando)
            self.cola_listos.remove(self.ejecutando)
            self.ejecutando.estado = d1["EJECUTANDO"]

    def planificar_cpu(self):
        # Planifica el uso de la CPU usando un Round Robin con quantum = 3
        # Se notifica a los procesos en LISTO y LISTOSUSPENDIDO que siguen esperando la CPU.
        for proceso in self.cola_listos:
            proceso.proceso_listo()

        if self.ejecutando:
            # Se notifica al proceso en EJECUTANDO que avanzó otro instante de tiempo.
            self.ejecutando.proceso_ejecutando()

            if self.ejecutando.terminado():
                self.terminar_procesos()
                self.asignar_cpu()
            elif self.quantum == 3:
                self.expropiar_proceso()
                self.asignar_cpu()
        else:
            self.asignar_cpu()

    def mostrar_estado(self):
        # Imprime el estado del simulador en un formato más sencillo con campo:valor.
        if self.ejecutando:
            print(f"CPU: P{self.ejecutando.id} ({self.ejecutando.estado})")
        else:
            print("CPU: None")

        if len(self.cola_listos) != 0:
            print("Cola de listos:")
            for proceso in self.cola_listos:
                print(f"  Proceso: P{proceso.id} ({proceso.estado})")
            print("Cola de Listos Suspendidos:")
            for proceso in self.cola_listos_suspendidos:
                print(f"  Proceso: P{proceso.id} ({proceso.estado})")
        else:
            print("Cola de listos: (vacía)")

        print(f"Tiempo: {self.t}")
        print(f"Quantum: {self.quantum}")

        # Imprimir tabla de particiones de memoria
        print("\nTabla de memoria: (valores en bytes)")
        for pos, part in enumerate(self.memoria_principal, start=1):
            mem_en_uso = part.proceso.memoria if part.proceso else 0
            pid = f"P{part.proceso.id}" if part.proceso else "-"
            presente = "Sí" if part.presente else "No"
            frag_interna = part.fragmetacion_interna()
            print(f"Partición {pos}:")
            print(f"  Presente: {presente}")
            print(f"  Proceso: {pid}")
            print(f"  Dir. Inicio: {part.dir_inicio}")
            print(f"  Tamaño: {part.memoria}")
            print(f"  Mem. en uso: {mem_en_uso}")
            print(f"  Fragamentacion. Interna: {frag_interna}")

        # Imprimir carga de trabajo
        print(f"\nCarga de trabajo: (grado de multiprogramación = {self.grado_multiprogramacion()})")
        print(self.carga)




