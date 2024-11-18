import os
import tkinter as tk
from tkinter import filedialog
from CargarProcesos import CargaTrabajo
from Simulador import Simulador
import pygame

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Sistema Operativo")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fuentes
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 32)

def abrir_archivo():
    """Abrir archivo de configuración de procesos usando Tkinter."""
    ubicacion_inicial = os.path.join(os.getcwd(), "./Archivos")
    archivo = filedialog.askopenfilename(initialdir=ubicacion_inicial, title="Seleccionar archivo")
    if archivo:
        carga_procesos = CargaTrabajo(archivo)
        return carga_procesos
    else:
        print("No se seleccionó ningún archivo.")
        return None

def dibujar_estado(simulador):
    """Dibuja el estado actual del simulador en la pantalla."""
    screen.fill(WHITE)

    # Título principal
    title = title_font.render("Simulador de Sistema Operativo", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # Memoria principal
    pygame.draw.rect(screen, BLACK, (50, 50, 300, 300), 2)
    mem_title = font.render("Memoria Principal", True, BLACK)
    screen.blit(mem_title, (150, 30))

    y_offset = 60
    for idx, part in enumerate(simulador.memoria_principal):
        color = RED if part.proceso else GREEN
        pygame.draw.rect(screen, color, (60, y_offset + idx * 40, 280, 30))
        text = font.render(
            f"Partición {idx + 1}: {'P' + str(part.proceso.id) if part.proceso else 'Libre'}",
            True, BLACK,
        )
        screen.blit(text, (70, y_offset + idx * 40 + 5))
        frag_text = font.render(
            f"Frag. Interna: {part.fragmetacion_interna()} bytes",
            True, BLACK,
        )
        screen.blit(frag_text, (70, y_offset + idx * 40 + 20))

    # Memoria secundaria
    pygame.draw.rect(screen, BLACK, (400, 50, 300, 300), 2)
    mem_sec_title = font.render("Memoria Secundaria", True, BLACK)
    screen.blit(mem_sec_title, (480, 30))

    y_offset = 60
    for idx, part in enumerate(simulador.memoria_secundaria):
        color = RED if part.proceso else GREEN
        pygame.draw.rect(screen, color, (410, y_offset + idx * 40, 280, 30))
        text = font.render(
            f"Partición {idx + 1}: {'P' + str(part.proceso.id) if part.proceso else 'Libre'}",
            True, BLACK,
        )
        screen.blit(text, (420, y_offset + idx * 40 + 5))
        frag_text = font.render(
            f"Frag. Interna: {part.fragmetacion_interna()} bytes",
            True, BLACK,
        )
        screen.blit(frag_text, (420, y_offset + idx * 40 + 20))

    # Cola de listos
    pygame.draw.rect(screen, BLACK, (50, 400, 300, 200), 2)
    cola_title = font.render("Cola de Listos", True, BLACK)
    screen.blit(cola_title, (150, 380))

    y_offset = 410
    if simulador.cola_listos:
        for idx, proceso in enumerate(simulador.cola_listos):
            text = font.render(f"P{proceso.id} (Tamaño: {proceso.memoria})", True, BLACK)
            screen.blit(text, (60, y_offset + idx * 30))
    else:
        text = font.render("Cola Vacía", True, BLACK)
        screen.blit(text, (60, y_offset + 5))

    # Proceso en ejecución
    pygame.draw.rect(screen, BLACK, (400, 400, 300, 80), 2)
    ejec_title = font.render("CPU en Ejecución", True, BLACK)
    screen.blit(ejec_title, (480, 380))

    if simulador.ejecutando:
        ejec_text = font.render(f"P{simulador.ejecutando.id} (Tamaño: {simulador.ejecutando.memoria})", True, BLACK)
    else:
        ejec_text = font.render("Ningún proceso en ejecución", True, BLACK)
    screen.blit(ejec_text, (410, 420))

    # Información general
    pygame.draw.rect(screen, BLACK, (50, 620, 700, 100), 2)
    info_title = font.render("Información General", True, BLACK)
    screen.blit(info_title, (330, 600))

    info_text = font.render(f"Tiempo: {simulador.t} | Quantum: {simulador.quantum}", True, BLACK)
    screen.blit(info_text, (60, 640))

    carga_text = font.render(f"Grado de multiprogramación: {simulador.grado_multiprogramacion()}", True, BLACK)
    screen.blit(carga_text, (60, 670))

    pygame.display.flip()

def main():
    # Crear ventana de Tkinter pero sin mostrarla
    root = tk.Tk()
    root.withdraw()

    procesos = abrir_archivo()
    if not procesos:
        return

    simulador = Simulador(procesos)

    # Simulación gráfica
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Avanzar ciclo con barra espaciadora
                    simulador.t += 1
                    simulador.quantum = (simulador.quantum % 3) + 1
                    for nuevo in simulador.procesos_nuevos():
                        simulador.admitir_proceso(nuevo)
                    simulador.planificar_cpu()
                elif event.key == pygame.K_q:  # Salir con 'q'
                    running = False

        # Dibujar estado actual
        dibujar_estado(simulador)

        # Terminar simulación si no hay procesos en la cola de listos, no hay proceso en ejecución y no hay procesos nuevos
        if not simulador.cola_listos and simulador.ejecutando is None and not simulador.procesos_nuevos():
            print("Simulación terminada. No hay más procesos en la cola de listos.")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()