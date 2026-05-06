from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QPen, QLinearGradient
)


# ──────────────────────────────────────────────
#  Widget de tanque individual (rectángulo animado)
# ──────────────────────────────────────────────
class TanqueWidget(QWidget):
    def __init__(self, nombre, color_agua=QColor(30, 144, 255), parent=None):
        super().__init__(parent)
        self.nombre = nombre
        self.nivel = 0.0
        self.volumen = 0.0
        self.color_agua = color_agua
        self.setMinimumSize(120, 250)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def set_nivel(self, nivel, volumen=0.0):
        self.nivel = max(0.0, min(nivel, 1.0))
        self.volumen = volumen
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margen = 10
        borde = 4

        # Contorno
        painter.setPen(QPen(QColor(60, 60, 80), borde))
        painter.setBrush(QColor(240, 245, 255))
        painter.drawRect(margen, margen, w - 2 * margen, h - 2 * margen - 30)

        # Agua con gradiente
        alto_tanque = h - 2 * margen - 30
        alto_agua = int(alto_tanque * self.nivel)
        y_agua = margen + alto_tanque - alto_agua

        if alto_agua > 0:
            grad = QLinearGradient(0, y_agua, 0, y_agua + alto_agua)
            grad.setColorAt(0, self.color_agua.lighter(130))
            grad.setColorAt(1, self.color_agua)
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawRect(
                margen + borde // 2,
                y_agua,
                w - 2 * margen - borde,
                alto_agua
            )

        # Etiqueta volumen
        painter.setPen(QColor(40, 40, 60))
        font = QFont("Courier New", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(
            margen, h - 30, w - 2 * margen, 28,
            Qt.AlignCenter,
            f"{self.nombre}  {self.volumen:.1f} L"
        )

        # Líneas de escala
        painter.setPen(QPen(QColor(180, 180, 200), 1, Qt.DashLine))
        for pct in [0.25, 0.50, 0.75]:
            y_lin = margen + int(alto_tanque * (1 - pct))
            painter.drawLine(margen, y_lin, w - margen, y_lin)
            painter.setPen(QColor(140, 140, 160))
            painter.setFont(QFont("Courier New", 7))
            painter.drawText(margen + 4, y_lin - 2, f"{int(pct * 100)}%")
            painter.setPen(QPen(QColor(180, 180, 200), 1, Qt.DashLine))


# ──────────────────────────────────────────────
#  Gráfica en tiempo real — 100% Qt, sin matplotlib
# ──────────────────────────────────────────────
class GraficaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(350, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.tiempos = []
        self.vol1 = []
        self.vol2 = []
        self.v1_est = 25.0
        self.v2_est = 50.0

        self._timer_grafica = QTimer()
        self._timer_grafica.timeout.connect(self.update)

    def set_estacionarios(self, v1_est, v2_est):
        self.v1_est = v1_est
        self.v2_est = v2_est

    def iniciar_refresco(self):
        self._timer_grafica.start(500)

    def detener_refresco(self):
        self._timer_grafica.stop()

    def agregar_punto(self, t, v1, v2):
        self.tiempos.append(t)
        self.vol1.append(v1)
        self.vol2.append(v2)

    def limpiar(self):
        self.tiempos.clear()
        self.vol1.clear()
        self.vol2.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        mx, my = 45, 20
        mb, mr = 30, 15
        area_w = w - mx - mr
        area_h = h - my - mb

        # Fondo
        painter.fillRect(0, 0, w, h, QColor("#16213e"))
        painter.fillRect(mx, my, area_w, area_h, QColor("#0f1b30"))

        if not self.tiempos:
            painter.setPen(QColor("#555577"))
            painter.setFont(QFont("Courier New", 9))
            painter.drawText(0, 0, w, h, Qt.AlignCenter, "Esperando datos...")
            return

        t_max = max(self.tiempos) if self.tiempos else 1
        v_max = self.v2_est * 1.15

        def px(t):
            return mx + int(t / t_max * area_w)

        def py(v):
            return my + area_h - int(v / v_max * area_h)

        # Grid horizontal
        for i in range(1, 5):
            yg = my + int(area_h * i / 4)
            painter.setPen(QPen(QColor("#223355"), 1, Qt.DashLine))
            painter.drawLine(mx, yg, mx + area_w, yg)
            val = v_max * (1 - i / 4)
            painter.setPen(QColor("#7788aa"))
            painter.setFont(QFont("Courier New", 7))
            painter.drawText(2, yg - 6, mx - 4, 14, Qt.AlignRight, f"{val:.0f}")

        # Líneas de estado estacionario
        painter.setPen(QPen(QColor("#ffff00"), 1, Qt.DashLine))
        painter.drawLine(mx, py(self.v1_est), mx + area_w, py(self.v1_est))
        painter.setPen(QPen(QColor("#ff9f43"), 1, Qt.DashLine))
        painter.drawLine(mx, py(self.v2_est), mx + area_w, py(self.v2_est))

        # Curva Tanque 1 (azul)
        if len(self.tiempos) > 1:
            painter.setPen(QPen(QColor("#1e90ff"), 2))
            for i in range(1, len(self.tiempos)):
                painter.drawLine(
                    px(self.tiempos[i - 1]), py(self.vol1[i - 1]),
                    px(self.tiempos[i]),     py(self.vol1[i])
                )

        # Curva Tanque 2 (rojo)
        if len(self.tiempos) > 1:
            painter.setPen(QPen(QColor("#ff6b6b"), 2))
            for i in range(1, len(self.tiempos)):
                painter.drawLine(
                    px(self.tiempos[i - 1]), py(self.vol2[i - 1]),
                    px(self.tiempos[i]),     py(self.vol2[i])
                )

        # Ejes
        painter.setPen(QPen(QColor("#8899bb"), 1))
        painter.drawLine(mx, my, mx, my + area_h)
        painter.drawLine(mx, my + area_h, mx + area_w, my + area_h)

        # Leyenda
        painter.setFont(QFont("Courier New", 8))
        leyenda = [
            (QColor("#1e90ff"), "Tanque 1"),
            (QColor("#ff6b6b"), "Tanque 2"),
            (QColor("#ffff00"), f"Eq.T1={self.v1_est:.0f}L"),
            (QColor("#ff9f43"), f"Eq.T2={self.v2_est:.0f}L"),
        ]
        lx = mx + 8
        for color, texto in leyenda:
            painter.setPen(QPen(color, 2))
            painter.drawLine(lx, my + 10, lx + 16, my + 10)
            painter.setPen(color)
            painter.drawText(lx + 20, my + 15, texto)
            lx += 90

        # Título
        painter.setPen(QColor("#aabbdd"))
        painter.setFont(QFont("Courier New", 8))
        painter.drawText(mx, 2, area_w, my, Qt.AlignCenter, "Evolución de volúmenes")

        # Eje X
        painter.setPen(QColor("#7788aa"))
        painter.drawText(mx, my + area_h + 2, area_w, mb, Qt.AlignCenter, "Tiempo (min)")


# ──────────────────────────────────────────────
#  Ventana principal
# ──────────────────────────────────────────────
class VistaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación de Tanques — Ecuaciones Diferenciales")
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #e0e0f0;
                font-family: 'Courier New';
            }
            QPushButton {
                background-color: #16213e;
                color: #e0e0f0;
                border: 2px solid #1e90ff;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-family: 'Courier New';
            }
            QPushButton:hover {
                background-color: #1e90ff;
                color: #fff;
            }
            QPushButton:disabled {
                border-color: #444;
                color: #666;
            }
            QLabel#tiempo {
                font-size: 15px;
                color: #a0c4ff;
                padding: 4px 10px;
                border: 1px solid #334;
                border-radius: 4px;
            }
        """)
        self._construir_ui()

    def _construir_ui(self):
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setSpacing(12)
        layout_raiz.setContentsMargins(18, 18, 18, 18)

        # Título
        titulo = QLabel("🧪 Simulación de Sistema de Dos Tanques")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 17px; font-weight: bold; color: #7eb8f7; padding: 6px;")
        layout_raiz.addWidget(titulo)

        # Fila superior: tanques + gráfica
        fila_superior = QHBoxLayout()
        fila_superior.setSpacing(20)

        self.tanque1 = TanqueWidget("Tanque 1", QColor(30, 144, 255))
        self.tanque2 = TanqueWidget("Tanque 2", QColor(255, 107, 107))
        fila_superior.addWidget(self.tanque1)
        fila_superior.addWidget(self.tanque2)

        self.grafica = GraficaWidget()
        fila_superior.addWidget(self.grafica)

        layout_raiz.addLayout(fila_superior)

        # Fila inferior: tiempo + botones
        fila_inferior = QHBoxLayout()
        fila_inferior.setSpacing(16)

        self.lbl_tiempo = QLabel("⏱  Tiempo: 0.00 min")
        self.lbl_tiempo.setObjectName("tiempo")
        fila_inferior.addWidget(self.lbl_tiempo)

        fila_inferior.addStretch()

        self.btn_iniciar = QPushButton("▶  Iniciar")
        self.btn_pausar = QPushButton("⏸  Pausar")
        self.btn_reiniciar = QPushButton("↺  Reiniciar")
        self.btn_pausar.setEnabled(False)

        fila_inferior.addWidget(self.btn_iniciar)
        fila_inferior.addWidget(self.btn_pausar)
        fila_inferior.addWidget(self.btn_reiniciar)

        layout_raiz.addLayout(fila_inferior)
        self.resize(860, 560)

    def actualizar_tiempo(self, minutos):
        self.lbl_tiempo.setText(f"⏱  Tiempo: {minutos:.2f} min")

    def set_estado_botones(self, corriendo: bool):
        self.btn_iniciar.setEnabled(not corriendo)
        self.btn_pausar.setEnabled(corriendo)