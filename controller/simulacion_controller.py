from PyQt5.QtCore import QTimer

class SimulacionController:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.dt = 0.1
        self.tiempo_transcurrido = 0.0    # ← faltaba esto

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)

    def iniciar(self):
        v1_max = self.modelo.tanque1.entrada / self.modelo.tanque1.k
        v2_max = (self.modelo.tanque1.k * v1_max) / self.modelo.tanque2.k
        self.vista.grafica.set_estacionarios(v1_max, v2_max)
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
        self.tiempo_transcurrido = 0.0
        self.modelo.tanque1.v = 0.0
        self.modelo.tanque2.v = 0.0
        self.vista.tanque1.set_nivel(0.0, 0.0)
        self.vista.tanque2.set_nivel(0.0, 0.0)
        self.vista.grafica.limpiar()
        self.vista.actualizar_tiempo(0.0)
        self.vista.set_estado_botones(corriendo=False)

    def actualizar(self):                          # ← faltaba este método
        self.modelo.actualizar(self.dt)
        self.tiempo_transcurrido += self.dt

        v1 = self.modelo.tanque1.v
        v2 = self.modelo.tanque2.v

        v1_max = self.modelo.tanque1.entrada / self.modelo.tanque1.k
        v2_max = (self.modelo.tanque1.k * v1_max) / self.modelo.tanque2.k

        nivel1 = min(v1 / v1_max, 1.0)
        nivel2 = min(v2 / v2_max, 1.0)

        self.vista.tanque1.set_nivel(nivel1, v1)
        self.vista.tanque2.set_nivel(nivel2, v2)
        self.vista.grafica.agregar_punto(self.tiempo_transcurrido, v1, v2)
        self.vista.actualizar_tiempo(self.tiempo_transcurrido)