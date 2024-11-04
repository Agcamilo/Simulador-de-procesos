# Definicion de los procesos
d1 = dict (
  NUEVO= "Nuevo",
  LYS= "Listo y Suspendido",
  LISTO= "Listo",
  EJECUTANDO = "Ejecutando",
  TERMINADO = "Terminado",
  INCORRECTO = "Incorrecto"
)


class Proceso:
    def __init__(self, np: int , tam_memo: int , ta:int , ti:int):
        self.numero_proceso = np
        self.tamaño = tam_memo
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