import sys
from PyQt5.QtWidgets import QApplication

from model.SistemaTanques import SistemasTanques
from view.vista import VistaPrincipal
from controller.simulacion_controller import SimulacionController

def main():
    app = QApplication(sys.argv)

    modelo = SistemasTanques(entrada=5, k1=0.2, k2=0.1)
    vista = VistaPrincipal()
    controlador = SimulacionController(modelo, vista)

    vista.btn_iniciar.clicked.connect(controlador.iniciar)
    vista.btn_pausar.clicked.connect(controlador.pausar)
    vista.btn_reiniciar.clicked.connect(controlador.reiniciar)

    vista.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()