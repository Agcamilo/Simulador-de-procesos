from typing import Optional

from Proceso import Proceso

#Definicion de las caracteríticas que tendrán las particiones 
class Particion:
    #Utilizamos Optional para indicar que el proceso puede ser nulo
    def __init__(self, id:int , memoria: int, proceso: Optional[Proceso] = None):
        
        self.id = id
        self.memoria = memoria
        self.proceso = proceso
        self.presente: bool = True
    
    def fragmetación_interna(self):
        
        if not self.proceso:
            return 0
        return self.memoria - self.proceso.memoria
    
    def clonar(self):
        """Instancia otra Particion de su mismo tamaño."""
        return Particion(self.memoria) 
        
