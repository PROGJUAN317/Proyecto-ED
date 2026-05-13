# ──────────────────────────────────────────────
#  main.py — Punto de entrada de la aplicación
#
#  Sigue el patrón MVC (Modelo - Vista - Controlador):
#
#    MODELO      : SistemasTanques — contiene las ecuaciones diferenciales
#                  y el estado físico del sistema (volúmenes)
#
#    VISTA       : VistaPrincipal  — interfaz gráfica, animación de tanques,
#                  gráfica y botones. No hace cálculos.
#
#    CONTROLADOR : SimulacionController — intermediario entre modelo y vista.
#                  Lee datos del modelo y los envía a la vista.
#                  Responde a los eventos de los botones.
#
#  Flujo de la aplicación:
#    1. Se crea el modelo con los parámetros físicos
#    2. Se crea la vista (ventana vacía)
#    3. Se crea el controlador conectando modelo y vista
#    4. Se conectan los botones de la vista al controlador
#    5. Se muestra la ventana y arranca el bucle de eventos de Qt
# ──────────────────────────────────────────────

import sys
from PyQt5.QtWidgets import QApplication

from model.SistemaTanques import SistemasTanques
from view.vista import VistaPrincipal
from controller.simulacion_controller import SimulacionController


def main():
    # Crear la aplicación Qt (requerido antes de cualquier widget)
    app = QApplication(sys.argv)

    # ── MODELO ──
    # Parámetros físicos del sistema:
    #   entrada = 5  L/min → flujo de agua que entra al tanque 1
    #   k1      = 0.2      → coeficiente de salida del tanque 1
    #   k2      = 0.1      → coeficiente de salida del tanque 2
    #
    # Estados estacionarios resultantes:
    #   V1* = entrada / k1        = 5 / 0.2       = 25 L
    #   V2* = (k1 × V1*) / k2    = (0.2×25) / 0.1 = 50 L
    modelo = SistemasTanques(entrada=5, k1=0.2, k2=0.1)

    # ── VISTA ──
    # Crea la ventana principal con los tanques, gráfica y botones
    vista = VistaPrincipal()

    # ── CONTROLADOR ──
    # Conecta el modelo y la vista, maneja el timer de simulación
    controlador = SimulacionController(modelo, vista)

    # ── CONECTAR BOTONES ──
    # Los botones de la vista llaman a los métodos del controlador
    vista.btn_iniciar.clicked.connect(controlador.iniciar)
    vista.btn_pausar.clicked.connect(controlador.pausar)
    vista.btn_reiniciar.clicked.connect(controlador.reiniciar)

    # ── MOSTRAR VENTANA ──
    vista.show()

    # Iniciar el bucle de eventos de Qt
    # El programa se mantiene aquí hasta que se cierre la ventana
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()