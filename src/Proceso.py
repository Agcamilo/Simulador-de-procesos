# Definicion de los procesos
d1 = dict (
  NUEVO= "Nuevo",
  LYS= "Listo y Suspendido",
  LISTO= "Listo",
  EJECUTANDO = "Ejecutando",
  TERMINADO = "Terminado",
  INCORRECTO = "Incorrecto",
  SUSPENDIDO = "Suspendido"
)


class Proceso:
    def __init__(self, id: int, ta:int , ti:int,memoria: int):
        if ti <= 0:
            raise ValueError(f"El tiempo de irrupción (ti) debe ser mayor a 0. Proceso ID: {id}")
        if ta < 0:
            raise ValueError(f"El tiempo de arribo (ta) debe ser mayor o igual a 0. Proceso ID: {id}")
        if memoria < 0:
            raise ValueError(f"Memoria Negativa? ._. . Proceso ID: {id}")
        if memoria == 0:
            raise ValueError(f"Memoria Nula? ._.  Proceso ID: {id}")
        self.id = id
        self.memoria = memoria
        self.estado = d1["NUEVO"]
        self.tiempo_arribo = ta
        self.tiempo_irrupcion = ti
        self.tiempo_ejecutando:int = 0 #Tiempo que lleva en la CPU
        self.tiempo_retorno:int  = 0 #Tiempo que tarda en ejecutarse
        self.tiempo_espera:int  = 0 #Tiempo que tarda en llegar a la CPU (se encuentra en cola de listos)
    def proceso_ejecutando(self):
        #Incrementa el tiempo de ejecución y de retorno del proceso en cada instante de tiempo
        self.tiempo_ejecutando += 1
        self.tiempo_retorno +=1     
        
    def proceso_listo(self):
        #Incrementa el tiempo de espera del proceso en cada instante de tiempo
        self.tiempo_espera += 1
        self.tiempo_retorno += 1
    


    def mostrar_progreso (self):
        # Muestra el progreso del proceso en la CPU
        return self.tiempo_ejecutando / self.tiempo_irrupcion * 100
    
    def terminado(self) -> bool:
        #Retorna True si el proceso cumplió su tiempo de irrupción y por ende terminó su tarea.
        return self.tiempo_irrupcion - self.tiempo_ejecutando <= 0
    
    def __repr__(self):
        return f"Proceso({self.id}, {self.tiempo_arribo}, {self.tiempo_irrupcion}, {self.memoria}, {self.estado}, {self.tiempo_ejecutando})"