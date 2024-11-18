import os
import tkinter as tk
from tkinter import filedialog
import pygame
from CargarProcesos import CargaTrabajo
from Simulador import Simulador

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

# Fuentes
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 32)


def progreso(porcentaje: float) -> str:
    """Muestra el progreso de un proceso mediante una barra de progreso."""
    cantidad = int((15 * porcentaje / 100))
    return f"{'█' * cantidad}{'_' * (15 - cantidad)} {round(porcentaje, 1)}%"


def abrir_archivo():
    """Abrir archivo de configuración de procesos usando Tkinter."""
    ubicacion_inicial = os.path.join(os.getcwd(), "./Archivos")
    archivo = filedialog.askopenfilename(initialdir=ubicacion_inicial, title="Seleccionar archivo")
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        carga_procesos = CargaTrabajo(archivo)
        return carga_procesos
    else:
        print("No se seleccionó ningún archivo.")
        return None


def dibujar_estado(simulador):
    """Dibuja el estado actual del simulador en la pantalla."""
    screen.fill(WHITE)

    # Título principal
    title = title_font.render("Simulador de Memoria", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # Memoria principal
    pygame.draw.rect(screen, BLACK, (50, 50, 300, 300), 2)
    mem_title = font.render("Memoria Principal", True, BLACK)
    screen.blit(mem_title, (140, 30))

    y_offset = 60
    for idx, part in enumerate(simulador.memoria_principal):
        color = GREEN if part.proceso else GRAY
        pygame.draw.rect(screen, color, (60, y_offset + idx * 40, 280, 30))
        pid_text = font.render(
            f"P{part.proceso.id}" if part.proceso else "Libre",
            True, BLACK,
        )
        frag_text = font.render(
            f"Frag. Interna: {part.fragmetacion_interna()}",
            True, RED if part.proceso else BLACK,
        )
        screen.blit(pid_text, (70, y_offset + idx * 40 + 5))
        screen.blit(frag_text, (70, y_offset + idx * 40 + 20))

    # Proceso en CPU
    pygame.draw.rect(screen, BLACK, (400, 50, 200, 100), 2)
    cpu_title = font.render("CPU", True, BLACK)
    screen.blit(cpu_title, (470, 30))

    if simulador.ejecutando:
        proceso_cpu = simulador.ejecutando
        proceso_cpu_text = font.render(
            f"P{proceso_cpu.id} - {progreso(proceso_cpu.mostrar_progreso())}",
            True, BLACK,
        )
        screen.blit(proceso_cpu_text, (420, 60))  # Ajusta la posición si es necesario
    else:
        no_proceso_text = font.render(
            "No hay proceso en la CPU", True, BLACK
        )
        screen.blit(no_proceso_text, (420, 60))

    # Cola de listos
    pygame.draw.rect(screen, BLACK, (650, 50, 300, 150), 2)
    listos_title = font.render("Cola de Listos", True, BLACK)
    screen.blit(listos_title, (750, 30))

    y_offset = 60
    for idx, proceso in enumerate(simulador.cola_listos):
        listos_text = font.render(
            f"P{proceso.id} - {progreso(proceso.mostrar_progreso())}",
            True, BLACK,
        )
        screen.blit(listos_text, (660, y_offset + idx * 30))

    # Cola de suspendidos
    pygame.draw.rect(screen, BLACK, (50, 400, 300, 150), 2)
    suspendidos_title = font.render("Cola de Suspendidos", True, BLACK)
    screen.blit(suspendidos_title, (110, 380))

    y_offset = 410
    for idx, proceso in enumerate(simulador.cola_suspendidos):
        suspendidos_text = font.render(f"P{proceso.id}", True, BLACK)
        screen.blit(suspendidos_text, (60, y_offset + idx * 30))

    # Información general
    info_text = font.render(f"Tiempo: {simulador.t} | Quantum: {simulador.quantum}", True, BLACK)
    screen.blit(info_text, (50, 600))

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
