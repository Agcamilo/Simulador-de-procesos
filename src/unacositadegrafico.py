import os
import tkinter as tk
from tkinter import filedialog
import pygame
from CargarProcesos import CargaTrabajo
from Simulador import Simulador
import time
import csv

# Inicializar PyGame
pygame.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Memoria")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)

# Fuentes
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 32)

def draw_rounded_rect(surface, color, rect, corner_radius):
    """Dibuja un rectángulo con bordes redondeados."""
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def draw_button(surface, rect, color, text, text_color, corner_radius=10, shadow=True):
    """Dibuja un botón con bordes redondeados y sombra."""
    if shadow:
        shadow_rect = rect.move(5, 5)
        draw_rounded_rect(surface, DARK_GRAY, shadow_rect, corner_radius)
    draw_rounded_rect(surface, color, rect, corner_radius)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def progreso(porcentaje: float) -> str:
    """Muestra el progreso de un proceso mediante una barra de progreso."""
    cantidad = int((15 * porcentaje / 100))
    return f"{'█' * cantidad}{'_' * (15 - cantidad)} {round(porcentaje, 1)}%"

def abrir_archivo():
    """Abrir archivo de configuración de procesos usando Tkinter."""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    ubicacion_inicial = os.path.join(os.getcwd(), "./Archivos")
    archivo = filedialog.askopenfilename(
        initialdir=ubicacion_inicial,
        title="Seleccionar archivo",
        filetypes=(
            ("Archivos CSV", "*.csv"),
            ("Todos los archivos", "*.*")
        )
    )
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        # Verifica que el archivo tenga la extensión .csv
        if not archivo.lower().endswith('.csv'):
            print("Error: El archivo debe tener la extensión .csv")
            mostrar_error(screen, "Error: El archivo debe tener la extensión .csv")
            return None
        try:
            # Verificar si el archivo está vacío
            with open(archivo, 'r') as f:
                reader = csv.reader(f)
                if not any(reader):
                    raise ValueError("El archivo CSV está vacío")
            carga_procesos = CargaTrabajo(archivo)
            return carga_procesos
        except ValueError as e:
            print(f"Error: {e}")
            mostrar_error(screen, f"Error: {e}")
            return None
    else:
        print("No se seleccionó ningún archivo.")
        return None

def mostrar_error(screen, mensaje):
    """Muestra un mensaje de error en la pantalla y un botón para reiniciar."""
    screen.fill(WHITE)  # Limpiar pantalla
    error_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 100)
    pygame.draw.rect(screen, RED, error_rect)
    pygame.draw.rect(screen, BLACK, error_rect, 2)  # Borde negro

    error_text = font.render(mensaje, True, WHITE)
    screen.blit(error_text, (error_rect.x + 20, error_rect.y + 40))

   # Dibujar botón de reiniciar
    boton_reiniciar_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 60, 100, 40)
    draw_button(screen, boton_reiniciar_rect, RED, "Reiniciar", WHITE)

    pygame.display.flip()

    return boton_reiniciar_rect

def dibujar_estado(simulador):
    """Dibuja el estado actual del simulador en la pantalla."""
    screen.fill(WHITE)

    # Título principal
    title = title_font.render("Simulador de Memoria", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # Memoria principal
    pygame.draw.rect(screen, BLACK, (50, 50, 350, 450), 2)  # Memoria más alta y ancha
    mem_title = font.render("Memoria Principal", True, BLACK)
    screen.blit(mem_title, (150, 30))

    # Ajuste de particiones en memoria
    partition_height = 100  # Altura uniforme de cada partición
    y_offset = 60
    for idx, part in enumerate(simulador.memoria_principal):
        color = GREEN if part.proceso else GRAY
        if idx == 0:
            partition_height = 150
        else:
            partition_height = 100
        pygame.draw.rect(screen, color, (60, y_offset + idx * partition_height, 330, partition_height - 10))  # Más ancho y espacio entre particiones
        pid_text = font.render(
            f"P{part.proceso.id}" if part.proceso else "Libre",
            True, BLACK,
        )
        frag_text = font.render(
            f"Frag. Interna: {part.fragmetacion_interna()}",
            True, RED if part.proceso else BLACK,
        )
        screen.blit(pid_text, (70, y_offset + idx * partition_height + 10))
        screen.blit(frag_text, (70, y_offset + idx * partition_height + 40))

    # Proceso en CPU
    pygame.draw.rect(screen, BLACK, (450, 50, 300, 150), 2)  # Más ancho para texto
    cpu_title = font.render("CPU", True, BLACK)
    screen.blit(cpu_title, (570, 30))

    if simulador.ejecutando:
        proceso_cpu = simulador.ejecutando
        proceso_cpu_text = font.render(
            f"P{proceso_cpu.id} - {progreso(proceso_cpu.mostrar_progreso())}",
            True, BLACK,
        )
        screen.blit(proceso_cpu_text, (460, 90))  # Centrado dentro del área de CPU
    else:
        no_proceso_text = font.render("No hay proceso en la CPU", True, BLACK)
        screen.blit(no_proceso_text, (460, 90))

    # Cola de listos
    pygame.draw.rect(screen, BLACK, (800, 50, 350, 200), 2)  # Más grande para cola
    listos_title = font.render("Cola de Listos", True, BLACK)
    screen.blit(listos_title, (930, 30))

    y_offset = 60
    for idx, proceso in enumerate(simulador.cola_listos):
        listos_text = font.render(
            f"P{proceso.id} - {progreso(proceso.mostrar_progreso())}",
            True, BLACK,
        )
        screen.blit(listos_text, (810, y_offset + idx * 30))

    # Cola de suspendidos
    pygame.draw.rect(screen, BLACK, (50, 520, 350, 200), 2)  # Ajustada proporcionalmente
    suspendidos_title = font.render("Cola de Nuevos", True, BLACK)
    screen.blit(suspendidos_title, (140, 500))

    y_offset = 530
    for idx, proceso in enumerate(simulador.cola_nuevos):
        suspendidos_text = font.render(f"P{proceso.id}", True, BLACK)
        screen.blit(suspendidos_text, (60, y_offset + idx * 30))


    #Cola de nuevos 
    pygame.draw.rect(screen, BLACK, (450, 220, 300, 200), 2)  # Ajustada proporcionalmente
    nuevos_title = font.render("Cola de Supendidos", True, BLACK)
    screen.blit(nuevos_title, (540, 200))

    y_offset = 230
    for idx, proceso in enumerate(simulador.cola_suspendidos):
        nuevos_text = font.render(f"P{proceso.id}", True, BLACK)
        screen.blit(nuevos_text, (460, y_offset + idx * 30))


    # Información general
    info_text = font.render(f"Tiempo: {simulador.t} | Quantum: {simulador.quantum}", True, BLACK)
    screen.blit(info_text, (50, 750))

    # Botón para avanzar ciclo
    pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 50, HEIGHT - 100, 100, 40))
    btn_text = font.render("Avanzar", True, WHITE)
    screen.blit(btn_text, (WIDTH // 2 - btn_text.get_width() // 2, HEIGHT - 90))

    pygame.display.flip()

def dibujar_procesos_cargados(screen, procesos):
    """Dibuja los procesos cargados inicialmente en pantalla."""
    pygame.draw.rect(screen, BLACK, (50, 700, 1100, 80), 2)  # Rectángulo para mostrar procesos
    title_text = font.render("Procesos cargados:", True, BLACK)
    screen.blit(title_text, (60, 680))

    # Mostrar IDs de los procesos
    x_offset = 60
    for idx, proceso in enumerate(procesos):
        proceso_text = font.render(f"P{proceso.id} (Tamaño: {proceso.memoria})", True, BLACK)
        screen.blit(proceso_text, (x_offset, 720))
        x_offset += 200  # Espaciado entre textos

def dibujar_reporte_final(screen, simulador):
    """Dibuja el reporte final en pantalla al terminar la simulación."""
    screen.fill(WHITE)  # Limpiar pantalla
    title = title_font.render("Reporte Final", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    y_offset = 60
    tiempo_espera_promedio = 0
    tiempo_retorno_promedio = 0

    for idx, p in enumerate(simulador.carga.procesos):
        reporte_text = font.render(
            f"P{p.id} - Espera: {p.tiempo_espera} - Retorno: {p.tiempo_retorno}",
            True,
            BLACK,
        )
        screen.blit(reporte_text, (60, y_offset + idx * 30))
        tiempo_espera_promedio += p.tiempo_espera
        tiempo_retorno_promedio += p.tiempo_retorno

    # Mostrar promedios
    y_offset += len(simulador.carga.procesos) * 30 + 20
    promedio_espera_text = font.render(
        f"Tiempo de espera promedio: {tiempo_espera_promedio / len(simulador.carga.procesos):.2f}",
        True,
        BLACK,
    )
    promedio_retorno_text = font.render(
        f"Tiempo de retorno promedio: {tiempo_retorno_promedio / len(simulador.carga.procesos):.2f}",
        True,
        BLACK,
    )
    rendimiento_text = font.render(
        f"Rendimiento: {len(simulador.carga.procesos) / simulador.t:.2f} procesos por unidad de tiempo",
        True,
        BLACK,
    )
    screen.blit(promedio_espera_text, (60, y_offset))
    screen.blit(promedio_retorno_text, (60, y_offset + 30))
    screen.blit(rendimiento_text, (60, y_offset + 60))

    pygame.display.flip()

def mostrar_procesos_iniciales(procesos):
    """Muestra todos los procesos cargados antes de iniciar la simulación."""
    print("\n=== Procesos Cargados ===")
    for p in procesos.procesos:
        print(f"ID: {p.id}, Tamaño: {p.memoria}, TA: {p.tiempo_arribo}, TI: {p.tiempo_irrupcion}")
    print("=========================\n")

def main():
    def reiniciar_programa():
        main()

    # Crear ventana de Tkinter pero sin mostrarla
    root = tk.Tk()
    root.withdraw()

    procesos = None
    simulador = None
    reporte_mostrado = False
    procesos_cargados = False  # Indica si los procesos iniciales ya fueron dibujados
    boton_cargar_clicked = False  # Flag to track if the "Cargar" button has been clicked

    # Coordenadas de los botones
    boton_cargar_rect = pygame.Rect(50, HEIGHT - 100, 100, 40)
    boton_avanzar_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 100, 100, 40)

    # Dibujar botones una vez
    if not boton_cargar_clicked:
        draw_button(screen, boton_cargar_rect, GREEN, "Cargar", WHITE)

    draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)

    pygame.display.flip()

    # Inicializar Pygame
    running = True
    boton_reiniciar_rect = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Detectar clics del mouse
                if boton_cargar_rect.collidepoint(event.pos) and not boton_cargar_clicked:  # Clic en el botón "Cargar"
                    archivo = filedialog.askopenfilename(
                        title="Seleccionar archivo de procesos",
                        filetypes=[("Todos los archivos", "*.*")]
                    )
                    if archivo:  # Si se seleccionó un archivo
                        # Verifica que el archivo tenga la extensión .csv
                        if not archivo.lower().endswith('.csv'):
                            print("Error: El archivo debe tener la extensión .csv")
                            boton_reiniciar_rect = mostrar_error(screen, "Error: El archivo debe tener la extensión .csv")
                            screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
                            break
                        try:
                            # Verificar si el archivo está vacío
                            with open(archivo, 'r') as f:
                                reader = csv.reader(f)
                                if not any(reader):
                                    raise ValueError("El archivo CSV está vacío")
                            procesos = CargaTrabajo(archivo)
                            mostrar_procesos_iniciales(procesos)  # Mostrar todos los procesos cargados
                            simulador = Simulador(procesos)
                            procesos_cargados = False  # Permitir que se dibujen los procesos nuevamente
                            boton_cargar_clicked = True  # Set the flag to True after clicking the button
                            screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
                            dibujar_estado(simulador)
                            draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)
                            pygame.display.flip()
                        except ValueError as e:
                            print(f"Error: {e}")
                            boton_reiniciar_rect = mostrar_error(screen, f"Error: {e}")
                            screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
                            break
                elif boton_avanzar_rect.collidepoint(event.pos) and simulador:  # Clic en "Avanzar"
                    simulador.t += 1
                    simulador.quantum = (simulador.quantum % 3) + 1
                    for nuevo in simulador.procesos_nuevos():
                        simulador.admitir_proceso(nuevo)
                    simulador.planificar_cpu()
                    screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
                    dibujar_estado(simulador)
                    draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)
                    pygame.display.flip()
                elif boton_reiniciar_rect and boton_reiniciar_rect.collidepoint(event.pos):  # Clic en "Reiniciar"
                    reiniciar_programa()
                    return
            elif event.type == pygame.KEYDOWN:  # Tecla para avanzar (opcional)
                if event.key == pygame.K_SPACE and simulador:  # Avanzar ciclo con barra espaciadora
                    simulador.t += 1
                    simulador.quantum = (simulador.quantum % 3) + 1
                    for nuevo in simulador.procesos_nuevos():
                        simulador.admitir_proceso(nuevo)
                    simulador.planificar_cpu()
                    screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
                    dibujar_estado(simulador)
                    draw_button(screen, boton_avanzar_rect, BLUE, "Avanzar", WHITE)
                    pygame.display.flip()

        # Dibujar estado actual si aún hay procesos
        if simulador and not reporte_mostrado:
            screen.fill(WHITE)  # Limpiar pantalla para evitar parpadeo
            dibujar_estado(simulador)

            # Mostrar procesos cargados solo una vez
            if not procesos_cargados:
                dibujar_procesos_cargados(screen, procesos.procesos)
                procesos_cargados = True

        # Terminar simulación si no hay más procesos pendientes
        if simulador and not simulador.cola_listos and not simulador.ejecutando and not simulador.procesos_nuevos():
            if not reporte_mostrado:
                print("Simulación terminada. Mostrando reporte final.")
                dibujar_reporte_final(screen, simulador)
                reporte_mostrado = True

    pygame.quit()

if __name__ == "__main__":
    main()