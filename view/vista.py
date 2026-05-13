from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSizePolicy, QDialog, QFormLayout,
    QDoubleSpinBox, QDialogButtonBox, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QLinearGradient


# ──────────────────────────────────────────────
#  TanqueWidget
# ──────────────────────────────────────────────
class TanqueWidget(QWidget):
    def __init__(self, nombre, color_agua=QColor(30, 144, 255), parent=None):
        super().__init__(parent)
        self.nombre = nombre
        self.nivel = 0.0
        self.volumen = 0.0
        self.v_max = 1.0
        self.color_agua = color_agua
        self.setMinimumSize(120, 250)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def set_nivel(self, nivel, volumen=0.0, v_max=None):
        self.nivel = max(0.0, min(nivel, 1.0))
        self.volumen = volumen
        if v_max is not None:
            self.v_max = v_max
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margen, borde = 10, 4

        # Contorno del tanque
        painter.setPen(QPen(QColor(60, 60, 80), borde))
        painter.setBrush(QColor(240, 245, 255))
        painter.drawRect(margen, margen, w - 2*margen, h - 2*margen - 40)

        alto_tanque = h - 2*margen - 40
        alto_agua = int(alto_tanque * self.nivel)
        y_agua = margen + alto_tanque - alto_agua

        if alto_agua > 0:
            grad = QLinearGradient(0, y_agua, 0, y_agua + alto_agua)
            grad.setColorAt(0, self.color_agua.lighter(130))
            grad.setColorAt(1, self.color_agua)
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawRect(margen + borde//2, y_agua,
                             w - 2*margen - borde, alto_agua)

        # Etiqueta: nombre y volumen actual / máximo — blanco y grande
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Courier New", 11, QFont.Bold))
        painter.drawText(margen, h-44, w-2*margen, 22,
                         Qt.AlignCenter, f"{self.nombre}")
        painter.setFont(QFont("Courier New", 10, QFont.Bold))
        painter.drawText(margen, h-22, w-2*margen, 22,
                         Qt.AlignCenter,
                         f"{self.volumen:.2f} / {self.v_max:.1f} L")

        # Líneas de escala (25 %, 50 %, 75 %)
        painter.setPen(QPen(QColor(180, 180, 200), 1, Qt.DashLine))
        for pct in [0.25, 0.50, 0.75]:
            y_lin = margen + int(alto_tanque * (1 - pct))
            painter.drawLine(margen, y_lin, w - margen, y_lin)
            painter.setPen(QColor(140, 140, 160))
            painter.setFont(QFont("Courier New", 7))
            painter.drawText(margen+4, y_lin-2, f"{int(pct*100)}%")
            painter.setPen(QPen(QColor(180, 180, 200), 1, Qt.DashLine))


# ──────────────────────────────────────────────
#  GraficaWidget
# ──────────────────────────────────────────────
class GraficaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(350, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tiempos, self.vol1, self.vol2 = [], [], []
        self.v1_obj = 5.0
        self.v2_obj = 5.0
        self._timer_grafica = QTimer()
        self._timer_grafica.timeout.connect(self.update)

    def set_objetivos(self, v1_obj, v2_obj):
        self.v1_obj = v1_obj
        self.v2_obj = v2_obj

    def set_estacionarios(self, v1, v2):
        self.set_objetivos(v1, v2)

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
        w, h = self.width(), self.height()
        mx, my, mb, mr = 50, 20, 30, 15
        area_w = w - mx - mr
        area_h = h - my - mb

        painter.fillRect(0, 0, w, h, QColor("#16213e"))
        painter.fillRect(mx, my, area_w, area_h, QColor("#0f1b30"))

        if not self.tiempos:
            painter.setPen(QColor("#555577"))
            painter.setFont(QFont("Courier New", 9))
            painter.drawText(0, 0, w, h, Qt.AlignCenter, "Esperando datos...")
            return

        t_max = max(self.tiempos)
        # Eje Y: cubre hasta un 15 % más del mayor volumen a mostrar
        v_max_datos = max(max(self.vol1 or [0]), max(self.vol2 or [0]),
                          self.v1_obj, self.v2_obj)
        v_max = v_max_datos * 1.15

        def px(t):
            if t_max == 0:
                return mx
            return mx + int(t / t_max * area_w)

        def py(v):
            if v_max == 0:
                return my + area_h
            return my + area_h - int(v / v_max * area_h)

        # Grid horizontal
        for i in range(1, 5):
            yg = my + int(area_h * i / 4)
            painter.setPen(QPen(QColor("#223355"), 1, Qt.DashLine))
            painter.drawLine(mx, yg, mx + area_w, yg)
            val = v_max * (1 - i / 4)
            painter.setPen(QColor("#7788aa"))
            painter.setFont(QFont("Courier New", 7))
            painter.drawText(2, yg-6, mx-4, 14, Qt.AlignRight, f"{val:.2f}")

        # Línea de volumen objetivo T1 (amarilla)
        painter.setPen(QPen(QColor("#ffff00"), 1, Qt.DashLine))
        painter.drawLine(mx, py(self.v1_obj), mx + area_w, py(self.v1_obj))
        # Línea de volumen objetivo T2 (naranja)
        painter.setPen(QPen(QColor("#ff9f43"), 1, Qt.DashLine))
        painter.drawLine(mx, py(self.v2_obj), mx + area_w, py(self.v2_obj))

        # Curva Tanque 1 (azul)
        if len(self.tiempos) > 1:
            painter.setPen(QPen(QColor("#1e90ff"), 2))
            for i in range(1, len(self.tiempos)):
                painter.drawLine(px(self.tiempos[i-1]), py(self.vol1[i-1]),
                                 px(self.tiempos[i]),   py(self.vol1[i]))

        # Curva Tanque 2 (rojo)
        if len(self.tiempos) > 1:
            painter.setPen(QPen(QColor("#ff6b6b"), 2))
            for i in range(1, len(self.tiempos)):
                painter.drawLine(px(self.tiempos[i-1]), py(self.vol2[i-1]),
                                 px(self.tiempos[i]),   py(self.vol2[i]))

        # Ejes
        painter.setPen(QPen(QColor("#8899bb"), 1))
        painter.drawLine(mx, my, mx, my + area_h)
        painter.drawLine(mx, my + area_h, mx + area_w, my + area_h)

        # Marcas y valores en el eje X (tiempo)
        num_marcas_x = 5
        for i in range(num_marcas_x + 1):
            xg = mx + int(area_w * i / num_marcas_x)
            t_val = t_max * i / num_marcas_x
            # línea de grid vertical
            if i > 0:
                painter.setPen(QPen(QColor("#223355"), 1, Qt.DashLine))
                painter.drawLine(xg, my, xg, my + area_h)
            # marca sobre el eje
            painter.setPen(QPen(QColor("#8899bb"), 1))
            painter.drawLine(xg, my + area_h, xg, my + area_h + 4)
            # valor numérico
            painter.setPen(QColor("#7788aa"))
            painter.setFont(QFont("Courier New", 7))
            lbl = f"{t_val:.1f}"
            painter.drawText(xg - 16, my + area_h + 5, 32, 14, Qt.AlignCenter, lbl)

        # Leyenda
        lx = mx + 8
        for color, texto in [
            (QColor("#1e90ff"), "Tanque 1"),
            (QColor("#ff6b6b"), "Tanque 2"),
            (QColor("#ffff00"), f"V_max T1={self.v1_obj:.2f}L"),
            (QColor("#ff9f43"), f"V_max T2={self.v2_obj:.2f}L"),
        ]:
            painter.setPen(QPen(color, 2))
            painter.drawLine(lx, my+10, lx+16, my+10)
            painter.setPen(color)
            painter.setFont(QFont("Courier New", 8))
            painter.drawText(lx+20, my+15, texto)
            lx += 100

        painter.setPen(QColor("#aabbdd"))
        painter.setFont(QFont("Courier New", 8))
        painter.drawText(mx, 2, area_w, my, Qt.AlignCenter, "Evolución de volúmenes")
        painter.setPen(QColor("#7788aa"))
        painter.setFont(QFont("Courier New", 8))
        painter.drawText(mx, my + area_h + 18, area_w, 14, Qt.AlignCenter, "Tiempo (min)")


# ──────────────────────────────────────────────
#  VentanaConfig
#
#  El usuario configura:
#    - Entrada de agua (L/min)
#    - v1_max: capacidad física del tanque 1 (L) — hasta aquí se llena
#    - k1:     coeficiente de salida del tanque 1
#    - v2_max: capacidad física del tanque 2 (L)
#    - k2:     coeficiente de salida del tanque 2
#
#  El panel informativo muestra en tiempo real el equilibrio teórico,
#  y si el tanque se llenará antes de llegar al equilibrio.
# ──────────────────────────────────────────────
class VentanaConfig(QDialog):
    def __init__(self, valores_actuales, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙  Configuración de parámetros")
        self.setMinimumWidth(460)
        self.setStyleSheet("""
            QDialog  { background-color: #1a1a2e; color: #e0e0f0; }
            QGroupBox {
                color: #a0c4ff;
                font-family: 'Courier New';
                font-size: 12px;
                border: 1px solid #334466;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 6px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
            QLabel {
                color: #a0c4ff;
                font-family: 'Courier New';
                font-size: 12px;
            }
            QDoubleSpinBox {
                background-color: #16213e;
                color: #e0e0f0;
                border: 1px solid #1e90ff;
                border-radius: 4px;
                padding: 4px 8px;
                font-family: 'Courier New';
                font-size: 12px;
                min-width: 110px;
            }
            QDoubleSpinBox:focus { border: 1px solid #7eb8f7; }
            QPushButton {
                background-color: #16213e;
                color: #e0e0f0;
                border: 2px solid #1e90ff;
                border-radius: 6px;
                padding: 6px 18px;
                font-family: 'Courier New';
                font-size: 12px;
            }
            QPushButton:hover { background-color: #1e90ff; color: #fff; }
        """)
        self._construir_ui(valores_actuales)

    def _spin(self, valor, minimo, maximo, paso=0.1, decimales=3):
        sb = QDoubleSpinBox()
        sb.setRange(minimo, maximo)
        sb.setSingleStep(paso)
        sb.setDecimals(decimales)
        sb.setValue(valor)
        return sb

    def _construir_ui(self, v):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Configura los parámetros del sistema")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #7eb8f7; font-size: 13px; font-weight: bold;")
        layout.addWidget(titulo)

        # ── Entrada de agua ──────────────────────────────────────
        grp_entrada = QGroupBox("Flujo de entrada")
        form_e = QFormLayout(grp_entrada)
        form_e.setSpacing(8)
        form_e.setLabelAlignment(Qt.AlignRight)
        self.spin_entrada = self._spin(v['entrada'], 0.01, 200.0, 0.5, 3)
        form_e.addRow("Entrada (L/min):", self.spin_entrada)
        layout.addWidget(grp_entrada)

        # ── Tanque 1 ─────────────────────────────────────────────
        grp_t1 = QGroupBox("🔵  Tanque 1")
        grp_t1.setStyleSheet(grp_t1.styleSheet() +
                             "QGroupBox { border-color: #1e90ff; color: #1e90ff; }")
        form_t1 = QFormLayout(grp_t1)
        form_t1.setSpacing(8)
        form_t1.setLabelAlignment(Qt.AlignRight)

        self.spin_v1 = self._spin(v['v1_max'], 0.1, 1000.0, 0.5, 2)
        self.spin_k1 = self._spin(v['k1'],     0.001, 50.0, 0.001, 4)

        lbl_v1 = QLabel("Volumen máximo T1 (L):")
        lbl_k1 = QLabel("k1 — coef. salida válvula:")
        lbl_v1.setToolTip("Capacidad física del tanque 1. El agua no superará este valor.")
        lbl_k1.setToolTip("Flujo_salida = k1 × V1.  Mayor k1 → sale más rápido → se llena menos.")
        form_t1.addRow(lbl_v1, self.spin_v1)
        form_t1.addRow(lbl_k1, self.spin_k1)
        layout.addWidget(grp_t1)

        # ── Tanque 2 ─────────────────────────────────────────────
        grp_t2 = QGroupBox("🔴  Tanque 2")
        grp_t2.setStyleSheet(grp_t2.styleSheet() +
                             "QGroupBox { border-color: #ff6b6b; color: #ff6b6b; }")
        form_t2 = QFormLayout(grp_t2)
        form_t2.setSpacing(8)
        form_t2.setLabelAlignment(Qt.AlignRight)

        self.spin_v2 = self._spin(v['v2_max'], 0.1, 1000.0, 0.5, 2)
        self.spin_k2 = self._spin(v['k2'],     0.001, 50.0, 0.001, 4)

        lbl_v2 = QLabel("Volumen máximo T2 (L):")
        lbl_k2 = QLabel("k2 — coef. salida válvula:")
        lbl_v2.setToolTip("Capacidad física del tanque 2.")
        lbl_k2.setToolTip("Flujo_salida = k2 × V2.  Mayor k2 → sale más rápido → se llena menos.")
        form_t2.addRow(lbl_v2, self.spin_v2)
        form_t2.addRow(lbl_k2, self.spin_k2)
        layout.addWidget(grp_t2)

        # ── Panel informativo en tiempo real ─────────────────────
        self.lbl_info = QLabel("")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setStyleSheet(
            "color: #00ff99; font-size: 11px; font-family: 'Courier New';"
            "border: 1px solid #00ff99; border-radius: 4px; padding: 8px;"
        )
        layout.addWidget(self.lbl_info)

        # Actualizar info al cambiar cualquier campo
        for sp in [self.spin_entrada, self.spin_k1, self.spin_k2,
                   self.spin_v1, self.spin_v2]:
            sp.valueChanged.connect(self._actualizar_info)
        self._actualizar_info()

        # ── Botones OK / Cancelar ────────────────────────────────
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("✔  Aplicar")
        botones.button(QDialogButtonBox.Cancel).setText("✘  Cancelar")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _actualizar_info(self):
        """
        Muestra en tiempo real el equilibrio teórico y el volumen real
        al que llegará cada tanque según la configuración actual.
        """
        entrada = self.spin_entrada.value()
        k1      = self.spin_k1.value()
        k2      = self.spin_k2.value()
        v1_max  = self.spin_v1.value()
        v2_max  = self.spin_v2.value()

        # Equilibrio teórico cuando dV/dt = 0
        v1_eq = entrada / k1
        # Flujo que llega a T2 en el equilibrio = k1 * V1_eq = entrada
        v2_eq = entrada / k2

        # Volumen real = limitado por la capacidad física del tanque
        v1_real = min(v1_eq, v1_max)
        v2_real = min(v2_eq, v2_max)

        estado1 = "🔒 lleno antes del equilibrio" if v1_eq > v1_max else "✅ se estabiliza en equilibrio"
        estado2 = "🔒 lleno antes del equilibrio" if v2_eq > v2_max else "✅ se estabiliza en equilibrio"

        self.lbl_info.setText(
            f"─── Tanque 1 ───────────────────────────────\n"
            f"  Equilibrio teórico : {v1_eq:.3f} L  {estado1}\n"
            f"  Se llenará hasta   : {v1_real:.3f} L\n"
            f"─── Tanque 2 ───────────────────────────────\n"
            f"  Equilibrio teórico : {v2_eq:.3f} L  {estado2}\n"
            f"  Se llenará hasta   : {v2_real:.3f} L"
        )

    def get_valores(self):
        """Retorna todos los parámetros configurados."""
        return {
            'entrada': self.spin_entrada.value(),
            'k1':      self.spin_k1.value(),
            'k2':      self.spin_k2.value(),
            'v1_max':  self.spin_v1.value(),
            'v2_max':  self.spin_v2.value(),
        }


# ──────────────────────────────────────────────
#  VistaPrincipal
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
            QPushButton:hover    { background-color: #1e90ff; color: #fff; }
            QPushButton:disabled { border-color: #444; color: #666; }
            QPushButton#btnConfig { border-color: #a0c4ff; }
            QPushButton#btnConfig:hover { background-color: #334466; }
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

        titulo = QLabel("🧪 Simulación de Sistema de Dos Tanques")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #7eb8f7; padding: 6px;")
        layout_raiz.addWidget(titulo)

        fila_superior = QHBoxLayout()
        fila_superior.setSpacing(20)

        self.tanque1 = TanqueWidget("Tanque 1", QColor(30, 144, 255))
        self.tanque2 = TanqueWidget("Tanque 2", QColor(255, 107, 107))
        fila_superior.addWidget(self.tanque1)
        fila_superior.addWidget(self.tanque2)

        self.grafica = GraficaWidget()
        fila_superior.addWidget(self.grafica)
        layout_raiz.addLayout(fila_superior)

        fila_inferior = QHBoxLayout()
        fila_inferior.setSpacing(16)

        self.lbl_tiempo = QLabel("⏱  Tiempo: 0.00 min")
        self.lbl_tiempo.setObjectName("tiempo")
        fila_inferior.addWidget(self.lbl_tiempo)
        fila_inferior.addStretch()

        self.btn_config    = QPushButton("⚙  Configurar")
        self.btn_iniciar   = QPushButton("▶  Iniciar")
        self.btn_pausar    = QPushButton("⏸  Pausar")
        self.btn_reiniciar = QPushButton("↺  Reiniciar")
        self.btn_config.setObjectName("btnConfig")
        self.btn_pausar.setEnabled(False)

        fila_inferior.addWidget(self.btn_config)
        fila_inferior.addWidget(self.btn_iniciar)
        fila_inferior.addWidget(self.btn_pausar)
        fila_inferior.addWidget(self.btn_reiniciar)
        layout_raiz.addLayout(fila_inferior)
        self.resize(960, 580)

    def actualizar_tiempo(self, minutos):
        self.lbl_tiempo.setText(f"⏱  Tiempo: {minutos:.2f} min")

    def set_estado_botones(self, corriendo: bool):
        self.btn_iniciar.setEnabled(not corriendo)
        self.btn_pausar.setEnabled(corriendo)
        self.btn_config.setEnabled(not corriendo)