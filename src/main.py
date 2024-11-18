import os
import tkinter as tk
from tkinter import filedialog
from CargarProcesos import CargaTrabajo
from Simulador import Simulador

def input_avanzar(prompt: str):
    """Pide al usuario una acción para avanzar o terminar la simulación."""
    try:
        inp = input(prompt)
        if inp == "q":
            exit(0)
    except EOFError:
        exit(0)

def abrir_archivo():
    # Obtener la ruta de la carpeta "Archivos" en el mismo directorio
    ubicacion_inicial = os.path.join(os.getcwd(), "./Archivos")
    archivo = filedialog.askopenfilename(initialdir=ubicacion_inicial, title="Seleccionar archivo")
    
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        CargaProcesos = CargaTrabajo(archivo)
        return CargaProcesos
    else:
        print("No se seleccionó ningún archivo.")

def menu():
        print("Menú:")
        print("1: Abrir archivo")
        print("0: Terminar programa")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            return abrir_archivo()
        elif opcion == "0":
            print("Terminando programa.")
        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    # Crear ventana de Tkinter pero sin mostrarla
    root = tk.Tk()
    root.withdraw()
    procesos = menu()
    
    simulador = Simulador(procesos)
    
    print("Los procesos cargados son:\n")
    print(procesos)
    print("Presione q + Enter para terminar el programa.")
    input_avanzar("Presione Enter para comenzar la simulación...")
    
    for nuevo in simulador.procesos_nuevos():
        simulador.admitir_proceso(nuevo)
    simulador.asignar_cpu()
    simulador.mostrar_estado()
    input_avanzar("Presione Enter para avanzar o q + Enter para salir...")
    
    while not simulador.terminados():
        simulador.t += 1
        simulador.quantum = (simulador.quantum % 3) + 1
        for nuevo in simulador.procesos_nuevos():
            simulador.admitir_proceso(nuevo)
        simulador.planificar_cpu()

        simulador.mostrar_estado()
        input_avanzar("Presione Enter para avanzar o q + Enter para salir...")

    simulador.reporte_grafico()
    print("\n================ ¡Simulación terminada! ================")
    
    
    
    
