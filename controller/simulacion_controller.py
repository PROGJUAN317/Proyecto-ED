# ──────────────────────────────────────────────
#  simulacion_controller.py — Controlador MVC
# ──────────────────────────────────────────────

from PyQt5.QtCore import QTimer
from view.vista import VentanaConfig


class SimulacionController:

    def __init__(self, modelo, vista, v1_max=5.0, v2_max=5.0):
        """
        Parámetros
        ----------
        modelo  : SistemasTanques
        vista   : VistaPrincipal
        v1_max  : capacidad física inicial del tanque 1 (L)
        v2_max  : capacidad física inicial del tanque 2 (L)
        """
        self.modelo = modelo
        self.vista  = vista
        self.dt     = 0.1
        self.tiempo_transcurrido = 0.0

        # ── Capacidad física de cada tanque ──────────────────────
        # Este valor es INDEPENDIENTE de k y del equilibrio teórico.
        # Es simplemente "hasta cuántos litros puede llenarse el tanque".
        self.v1_max = v1_max
        self.v2_max = v2_max

        # Timer principal: llama a actualizar() cada 50 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)

        # Conectar botón Configurar
        self.vista.btn_config.clicked.connect(self.abrir_config)

        # Inicializar la vista con los v_max correctos desde el principio
        self.vista.tanque1.set_nivel(0.0, 0.0, self.v1_max)
        self.vista.tanque2.set_nivel(0.0, 0.0, self.v2_max)

    # ── Configuración ──────────────────────────────────────────────────────
    def abrir_config(self):
        """
        Abre la ventana de configuración con los valores actuales.
        Si el usuario presiona Aplicar, actualiza el modelo y reinicia la vista.
        """
        valores_actuales = {
            'entrada': self.modelo.tanque1.entrada,
            'k1':      self.modelo.tanque1.k,
            'k2':      self.modelo.tanque2.k,
            'v1_max':  self.v1_max,
            'v2_max':  self.v2_max,
        }

        dialogo = VentanaConfig(valores_actuales, parent=self.vista)

        if dialogo.exec_() == VentanaConfig.Accepted:
            v = dialogo.get_valores()

            # Aplicar parámetros al modelo
            self.modelo.tanque1.entrada = v['entrada']
            self.modelo.tanque1.k       = v['k1']
            self.modelo.tanque2.k       = v['k2']

            # Guardar los volúmenes máximos tal como el usuario los escribió
            self.v1_max = v['v1_max']
            self.v2_max = v['v2_max']

            self._resetear()

    # ── Control de simulación ──────────────────────────────────────────────
    def iniciar(self):
        # Las líneas de referencia en la gráfica apuntan a los v_max del usuario
        self.vista.grafica.set_objetivos(self.v1_max, self.v2_max)
        self.timer.start(50)
        self.vista.grafica.iniciar_refresco()
        self.vista.set_estado_botones(corriendo=True)

    def pausar(self):
        self.timer.stop()
        self.vista.grafica.detener_refresco()
        self.vista.set_estado_botones(corriendo=False)

    def reiniciar(self):
        self.timer.stop()
        self.vista.grafica.detener_refresco()
        self._resetear()

    def _resetear(self):
        self.tiempo_transcurrido = 0.0
        self.modelo.tanque1.v = 0.0
        self.modelo.tanque2.v = 0.0

        # Pasar v_max actualizado a los widgets de tanque
        self.vista.tanque1.set_nivel(0.0, 0.0, self.v1_max)
        self.vista.tanque2.set_nivel(0.0, 0.0, self.v2_max)
        self.vista.grafica.set_objetivos(self.v1_max, self.v2_max)
        self.vista.grafica.limpiar()
        self.vista.actualizar_tiempo(0.0)
        self.vista.set_estado_botones(corriendo=False)

    # ── Paso de simulación ─────────────────────────────────────────────────
    def actualizar(self):
        """
        Avanza el modelo un paso dt y actualiza la vista.
        El nivel visual = volumen_actual / v_max  (entre 0 y 1).
        """
        self.modelo.actualizar(self.dt, self.v1_max, self.v2_max)
        self.tiempo_transcurrido += self.dt

        v1 = self.modelo.tanque1.v
        v2 = self.modelo.tanque2.v

        nivel1 = min(v1 / self.v1_max, 1.0) if self.v1_max > 0 else 0.0
        nivel2 = min(v2 / self.v2_max, 1.0) if self.v2_max > 0 else 0.0

        self.vista.tanque1.set_nivel(nivel1, v1, self.v1_max)
        self.vista.tanque2.set_nivel(nivel2, v2, self.v2_max)
        self.vista.grafica.agregar_punto(self.tiempo_transcurrido, v1, v2)
        self.vista.actualizar_tiempo(self.tiempo_transcurrido)