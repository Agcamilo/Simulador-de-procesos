from typing import Optional, List
from tabulate import tabulate
from Particion import Particion
from Proceso import Proceso
from CargarProcesos import CargaTrabajo

class Simulador:
    #Representa la simulacion.

    def __init__(self, carga: CargaTrabajo):
        self.carga = carga
        self.cola_listos: List[Proceso] = []
        self.ejecutando: Optional[Proceso] = None

        #Datos para la memoria
        p1= 250*1024 #KB * Byte
        p2= 150*1024
        p3= 50*1024
        self.memoria_principal : List[Particion]= [p1,p2,p3]
        self.memoria_secundaria : List[Particion] = []
        self.max_multiprogramacion: int = 5

        self.t: int = 0
        self.quantun: int = 0

    def terminados(self) -> bool:
        return self.carga.terminada()
    
    def grado_multiprogramacion(self) -> int:
        #etorna la cantidad de procesos alojados en memoria principal y virtual
        ejecutando = 1 if self.ejecutando else 0 #ejecutando
        return ejecutando + len(self.cola_listos) #

    def mem_secundaria_disponible(self) -> bool:
        #Retorna True si hay espacio disponible en memoria secundaria
        return self.grado_multiprogramacion() < self.max_multiprogramacion
    
    def procesos_nuevos(self) -> List[Proceso]:
        #Retorna una lista con los procesos que llegan en el tiempo actual
        return list(filter(lambda p: p.tiempo_arribo <= self.t and p.estado == "Nuevo", self.carga.procesos))
    
    def encontrar_particion(self, proceso: Proceso) -> Optional[Particion]:
        # Retorna una partición de memoria ocupada o libre para el proceso según el algoritmo worst-fit.
        peor_part: Optional[Particion] = None
        for part in self.memoria_principal:
            if part.memoria >= proceso.memoria:
                if peor_part is None or part.memoria > peor_part.memoria:
                    peor_part = part
    
        return peor_part
    
    def encontrar_particion_libre(self, proceso: Proceso) -> Optional[Particion]:
        #Retorna una partición de memoria libre para el proceso según el algoritmo worst-fit.
        peor_part: Optional[Particion] = None
    
        for part in self.memoria_principal:
            if part.proceso is None and part.memoria >= proceso.memoria:
                if peor_part is None or part.memoria > peor_part.memoria:
                    peor_part = part
    
        return peor_part
    
    def encontrar_particion_proceso(self, proceso: Proceso) -> Optional[Particion]:
        #Retorna la partición que está asignada al proceso pasado por parámetro.
        for part in self.memoria_principal + self.memoria_secundaria:
            if part.proceso == proceso:
                return part
            
    def encontrar_particion_victima(self, particion: Particion) -> Optional[Particion]:
        #Retorna la partición en memoria principal que debería reemplazarse por la partición ausente.
        for part in self.memoria_principal:
            if part.dir_inicio == particion.dir_inicio:
                return part
            
    def swap_in_particion(self, part: Particion):
       #Trae una partición ausente en memoria virtual a la memoria principal.
        #Si se requiere un swap out, la partición víctima será la del mismo tamaño que la ausente.

        self.memoria_secundaria.remove(part)
        part.presente = True

        victima = self.encontrar_particion_victima(part)
        if victima.proceso:
            # Si hay un proceso en la partición víctima, se hace un swap out.
            victima.proceso.estado = "Listo y Supendido"
            victima.presente = False
            self.memoria_secundaria.append(victima)
        
        index = self.memoria_principal.index(victima)
        self.memoria_principal[index] = part
        #Se actualiza la partición en memoria principal.

    def admitir_proceso(self, proceso: Proceso):
       #Asigna una partición de memoria (en MP o MV) al proceso, o lo rechaza si no hay disponibles.
        part = self.encontrar_particion_libre(proceso)
        if part and part.presente:
            part.proceso = proceso
            proceso.estado = "Listo"
            self.cola_listos.append(proceso)
            return  

        if self.mem_secundaria_disponible():
            part_ocupada = self.encontrar_particion(proceso)
            if part_ocupada is None:
                #El proceso no entra en ninguna particion, se lo denega para siempre
                print(f"Proceso {proceso.id} no entra en ninguna particion")
                proceso.estado = "Incorrecto"
                return 
            
        else:
            #Rechazar proceso, volvera a internar en el siguiente instante de tiempo
            print(f"Proceso {proceso.id} rechazado por falta de espacio")

        
    def terminar_procesos(self):
        #Termina el proceso en ejecución en la CPU y libera su partición de memoria asignada.
        part = self.encontrar_particion_proceso(self.ejecutando)
        part.proceso = None
        self.ejecutando.estado = "Terminado"
        self.ejecutando = None
        self.quantum = 0
    
    def expropiar_proceso(self):
        #Expropia el proceso en ejecución en la CPU y lo manda a la cola de listos.
        self.cola_listos.append(self.ejecutando)
        self.ejecutando.estado = "Listo"
        self.ejecutando = None

    def activar_proceso(self, proceso:Proceso):
        #Activa un proceso en la CPU y lo asigna a una partición de memoria.
        part = self.encontrar_particion_libre(proceso)
        if part is None:
            part = self.encontrar_particion_libre(proceso)
            if part and part.presente:
                part.proceso = proceso
                proceso.estado = "Listo"
                return  
            
            #Se le asigna una ya ocupada y se hace swap out a la victima

            part_ocupada = self.encontrar_particion(proceso)
            part= part_ocupada.clonar() #Se clona la particion ocupada
            part.proceso = proceso
            self.memoria_secundaria.append(part)
            proceso.estado = "Listo"

        if not part.presente:
            #Proceso estraba suspendido, se lo trae a MP
            self.swap_in_particion(part)

    def asignar_cpu(self):
        #Asigna la CPU al siguiente proceso de la cola de listos, y lo activa si está en mem virtual.
        if 0 == len(self.cola_listos):
            self.ejecutando = None
        else:
            self.ejecutando = self.cola_listos[0]
            self.activar_proceso(self.ejecutando)
            self.cola_listos.remove(self.ejecutando)
            self.ejecutando.estado = "Ejecutando"

    def planificar_cpu(self):
        #Planifica el uso de la CPU usando un Round Robin con quantum = 3
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
    #Imprime el estado del simulador en un formato más sencillo con campo:valor."""
    # Imprimir estado del procesador y de la cola de listos
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




