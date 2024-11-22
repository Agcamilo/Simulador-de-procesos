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

<<<<<<< Updated upstream
def menu():
        print("Menú:")
        print("1: Abrir archivo")
        print("0: Terminar programa")
        opcion = input("Selecciona una opción: ")
=======
def mostrar_error(screen, mensaje):
    """Muestra un mensaje de error en la pantalla y un botón para reiniciar."""
    screen.fill(WHITE)  # Limpiar pantalla
    error_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 50, 650, 100)
    pygame.draw.rect(screen, RED, error_rect)
    pygame.draw.rect(screen, BLACK, error_rect, 2)  # Borde negro
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    procesos = menu()
=======

    procesos = None
    simulador = None
    reporte_mostrado = False
    procesos_cargados = False  # Indica si los procesos iniciales ya fueron dibujados
    boton_cargar_clicked = False  # Flag para rastrear si se hizo clic en "Cargar"

    # Coordenadas de los botones
    boton_cargar_rect = pygame.Rect(50, HEIGHT - 100, 100, 40)
    boton_avanzar_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 100, 100, 40)

    # Configurar el fondo y título inicial
    screen.fill(CAFE)  # Fondo oscuro
    logo_path = os.path.join(os.getcwd(), "src", "Archivos", "logo.png")
    logo = pygame.image.load(logo_path)
    title_text = title_font.render("Simulador de Procesos - Cafe Colombiano", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    logo = pygame.transform.scale(logo,(250,200))
    screen.blit(logo,(490,100))
    screen.blit(title_text, title_rect)

    # Integrantes
    integrantes = ["INTEGRANTES DEL GRUPO:", "Aguirre, Camilo", "Boland Morley, Jeremias", "Casco, Ariel", "Petraccaro, Maximiliano"]

    for idx, integrante in enumerate(integrantes):
        integrante_text = font.render(integrante, True, WHITE)
        screen.blit(integrante_text, (WIDTH // 2 - integrante_text.get_width() // 2, HEIGHT // 2 + 50 + idx * 30))

    # Dibujar botones iniciales
    if not boton_cargar_clicked:
        draw_button(screen, boton_cargar_rect, GREEN, "Cargar", WHITE)

    pygame.display.flip()

    # Inicializar Pygame
    running = True
    boton_reiniciar_rect = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if boton_cargar_rect.collidepoint(event.pos) and not boton_cargar_clicked:
                    archivo = filedialog.askopenfilename(
                        title="Seleccionar archivo de procesos",
                        filetypes=[("Todos los archivos", "*.*")]
                    )
                    if archivo:
                        if not archivo.lower().endswith('.csv'):
                            print("Error: El archivo debe tener la extensión .csv")
                            boton_reiniciar_rect = mostrar_error(screen, "Error: El archivo debe tener la extensión .csv")
                            screen.fill(DARK_GRAY)
                            break
                        try:
                            with open(archivo, 'r') as f:
                                reader = csv.reader(f)
                                if not any(reader):
                                    raise ValueError("El archivo CSV está vacío")
                            procesos = CargaTrabajo(archivo)

                            if len(procesos.procesos) > 10:
                                raise ValueError("Cantidad de procesos excedidos")
                        
                            mostrar_procesos_iniciales(procesos)
                            simulador = Simulador(procesos)
                            procesos_cargados = False
                            boton_cargar_clicked = True
                            
                            # Mostrar estado inicial antes de permitir avanzar
                            screen.fill(WHITE)
                            for nuevo in simulador.procesos_nuevos():
                                simulador.admitir_proceso(nuevo)
                            simulador.asignar_cpu()
                            dibujar_estado(simulador)  # Mostrar estado inicial
                            
                            draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)
                            pygame.display.flip()
                            
                        except ValueError as e:
                            print(f"Error: {e}")
                            boton_reiniciar_rect = mostrar_error(screen, f"Error: {e}")
                            screen.fill(DARK_GRAY)
                            break
                elif boton_avanzar_rect.collidepoint(event.pos) and simulador:
                    simulador.t += 1
                    simulador.quantum = (simulador.quantum % 3) + 1
                    for nuevo in simulador.procesos_nuevos():
                        simulador.admitir_proceso(nuevo)
                    simulador.planificar_cpu()
                    screen.fill(WHITE)
                    dibujar_estado(simulador)
          
                    draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)
                    pygame.display.flip()
                elif boton_reiniciar_rect and boton_reiniciar_rect.collidepoint(event.pos):
                    reiniciar_programa()
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and simulador:
                    simulador.t += 1
                    simulador.quantum = (simulador.quantum % 3) + 1
                    for nuevo in simulador.procesos_nuevos():
                        simulador.admitir_proceso(nuevo)
                    simulador.planificar_cpu()
                    screen.fill(WHITE)
                    dibujar_estado(simulador)

                    draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)
                    pygame.display.flip()

        # Dibujar estado actual si aún hay procesos
        if simulador and not reporte_mostrado:
            screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
            dibujar_estado(simulador)
>>>>>>> Stashed changes
    
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

    print("\n================ ¡Simulación terminada! ================")
    
    
    
    
