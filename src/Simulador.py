from typing import Optional, List
from tabulate import tabulate
from Particion import Particion
from Proceso import Proceso
from CargarProcesos import CargaTrabajo
from Proceso import d1

# Define la función kb_a_bytes
def kb_a_bytes(kilobytes: int) -> int:
    return kilobytes * 1024

class Simulador:
    """Representa una simulación. Interconecta al resto de clases y se
    encarga de la planificación de la CPU y administración de memoria."""

    def __init__(self, carga: CargaTrabajo):
        """Inicializa un Simulador con una CargaTrabajo y una List[Particion] (memoria)."""
        self.carga = carga
        self.cola_listos: List[Proceso] = []
        self.cola_suspendidos: List[Proceso] = []
        self.ejecutando: Optional[Proceso] = None

        # Estructuras de datos para la memoria.
        p0 = Particion(0, kb_a_bytes(100))
        p1 = Particion(p0.dir_inicio + p0.memoria, kb_a_bytes(250))
        p2 = Particion(p1.dir_inicio + p1.memoria, kb_a_bytes(150))
        p3 = Particion(p2.dir_inicio + p2.memoria, kb_a_bytes(50))
        self.memoria_principal: List[Particion] = [p1, p2, p3]
        self.memoria_secundaria: List[Particion] = []
        

        self.t: int = 0
        self.quantum: int = 0

    def terminados(self) -> bool:
        return self.carga.terminada()

    def grado_multiprogramacion(self) -> int:
        """Retorna la cantidad de procesos alojados en memoria principal."""
        return len([part for part in self.memoria_principal if part.proceso is not None] ) + len([part for part in self.memoria_secundaria if part.proceso is not None])

    def mem_principal_disponible(self) -> bool:
        """Retorna True si hay espacio disponible en memoria principal."""
        return len([part for part in self.memoria_principal if part.proceso is not None] )  < 3

    def procesos_nuevos(self) -> List[Proceso]:
        """Retorna una lista con los procesos que llegan en el tiempo actual."""
        return list(filter(lambda p: p.tiempo_arribo <= self.t and p.estado == d1["NUEVO"], self.carga.procesos))

    def encontrar_particion_libre(self, proceso: Proceso) -> Optional[Particion]:
        """Retorna una partición de memoria libre para el proceso según el algoritmo worst-fit."""
        peor_part: Optional[Particion] = None
        for part in self.memoria_principal:
            if part.proceso is None and part.memoria >= proceso.memoria:
                if peor_part is None or part.memoria > peor_part.memoria:
                    peor_part = part
        return peor_part

    def encontrar_particion_proceso(self, proceso: Proceso) -> Optional[Particion]:
        """Retorna la partición que está asignada al proceso pasado por parámetro."""
        for part in self.memoria_principal + self.memoria_secundaria:
            if part.proceso == proceso:
                return part

    def swap_in_particion(self):
    #Mueve un proceso desde memoria secundaria a memoria principal.
        if self.memoria_secundaria:
            for part_secundaria in self.memoria_secundaria:
                if self.mem_principal_disponible():
                    for part_principal in self.memoria_principal:
                        if part_principal.proceso is None:
                            part_principal.proceso = part_secundaria.proceso
                            part_principal.proceso.estado = d1["LISTO"]
                            self.cola_suspendidos.remove(part_secundaria.proceso)
                            self.cola_listos.append(part_principal.proceso)
                            self.memoria_secundaria.remove(part_secundaria)
                            print(f"Proceso {part_principal.proceso.id} movido de memoria secundaria a principal.")
                            break

    def admitir_proceso(self, proceso: Proceso):
        """Asigna una partición de memoria principal o secundaria al proceso."""
        if self.mem_principal_disponible():
            part = self.encontrar_particion_libre(proceso)
            if part:
                part.proceso = proceso
                proceso.estado = d1["LISTO"]
                self.cola_listos.append(proceso)
                print(f"Proceso {proceso.id} admitido en memoria principal.")
            else:
                print(f"Proceso {proceso.id} no entra en ninguna partición.")
                proceso.estado = d1["INCORRECTO"]
        elif len(self.memoria_secundaria) < 2:
            # Si hay espacio en memoria secundaria, mover el proceso allí
            nueva_particion = Particion(0, proceso.memoria)
            nueva_particion.proceso = proceso
            proceso.estado = d1["SUSPENDIDO"]
            self.memoria_secundaria.append(nueva_particion)
            self.cola_suspendidos.append(proceso)
            print(f"Proceso {proceso.id} admitido en memoria secundaria.")
        else:
            print(f"Proceso {proceso.id} rechazado por falta de espacio en memoria.")

    def terminar_procesos(self):
        """Libera memoria principal y mueve un proceso de memoria secundaria."""
        if self.ejecutando is None:
            print("No hay proceso en ejecución.")
            return

        part = self.encontrar_particion_proceso(self.ejecutando)
        if part is not None:
            part.proceso = None
        self.ejecutando.estado = d1["TERMINADO"]
        print(f"Proceso {self.ejecutando.id} terminado y liberado de memoria principal.")
        self.ejecutando = None
        self.quantum = 0

        # Realizar swap in después de terminar el proceso
        self.swap_in_particion()

    def expropiar_proceso(self):
        """Expropia el proceso en ejecución en la CPU y lo manda a la cola de listos."""
        self.cola_listos.append(self.ejecutando)
        self.ejecutando.estado = d1["LISTO"]
        self.ejecutando = None

    def activar_proceso(self, proceso: Proceso):
        """Activa un proceso en la CPU y lo asigna a una partición de memoria."""
        part = self.encontrar_particion_libre(proceso)
        if part and part.presente:
            part.proceso = proceso
            proceso.estado = d1["LISTO"]
        else:
            print(f"Proceso {proceso.id} no puede ser activado porque no hay partición libre")

    def asignar_cpu(self):
        """Asigna la CPU al siguiente proceso de la cola de listos."""
        if 0 == len(self.cola_listos):
            self.ejecutando = None
        else:
            self.ejecutando = self.cola_listos.pop(0)
            self.ejecutando.estado = d1["EJECUTANDO"]

    def planificar_cpu(self):
        """Planifica el uso de la CPU usando un Round Robin con quantum = 3."""
        # Se notifica a los procesos en LISTO que siguen esperando la CPU.
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
        """Imprime el estado del simulador en un formato más sencillo con campo:valor."""
        if self.ejecutando:
            print(f"CPU: P{self.ejecutando.id} ({self.ejecutando.estado})")
        else:
            print("CPU: None")

        if len(self.cola_listos) != 0:
            print("Cola de listos:")
            for proceso in self.cola_listos:
                print(f"  Proceso: P{proceso.id} ({proceso.estado})")
        else:
            print("Cola de listos: (vacía)")

        if len(self.cola_suspendidos) != 0:
            print("Cola de suspendidos:")
            for pid in self.cola_suspendidos:
                print(f"  Proceso: P{pid.id} ({pid.estado})")
        print(f"Tiempo: {self.t}")
        print(f"Quantum: {self.quantum}")

        # Imprimir tabla de particiones de memoria
        print("\nTabla de memoria: (valores en bytes)")
        for pos, part in enumerate(self.memoria_principal + self.memoria_secundaria, start=1):
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
    
    def reporte_grafico(self):
        #Genera un reporte gráfico del estado del simulador.
        tiempo_espera_promedio = 0
        tiempo_retorno_promedio = 0
        for p in self.carga.procesos:
            print("tiempo de retorno del proceso",p.id,":", p.tiempo_retorno)      
            print("tiempo de espera del proceso",p.id,":", p.tiempo_espera)
            print("----------------------------------------------------------------")
            tiempo_espera_promedio += p.tiempo_espera
            tiempo_retorno_promedio += p.tiempo_retorno
            
        print("RESULTADOS PROMEDIOS:")
        print("tiempo de espera promedio es:", tiempo_espera_promedio/len(self.carga.procesos))
        print("tiempo de retorno promedio es:", tiempo_retorno_promedio/len(self.carga.procesos))

        print("Rendimiento del simulador:",(len(self.carga.procesos)/self.t))