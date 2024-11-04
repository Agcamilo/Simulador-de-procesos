import os
import tkinter as tk
from tkinter import filedialog
from CargarProcesos import CargaTrabajo

def abrir_archivo():
    # Obtener la ruta de la carpeta "Archivos" en el mismo directorio
    ubicacion_inicial = os.path.join(os.getcwd(), "./Archivos")
    archivo = filedialog.askopenfilename(initialdir=ubicacion_inicial, title="Seleccionar archivo")
    
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        CargaProcesos = CargaTrabajo(archivo)
    else:
        print("No se seleccionó ningún archivo.")

def menu():
        print("Menú:")
        print("1: Abrir archivo")
        print("0: Terminar programa")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            abrir_archivo()
        elif opcion == "0":
            print("Terminando programa.")
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    # Crear ventana de Tkinter pero sin mostrarla
    root = tk.Tk()
    root.withdraw()
    menu()
