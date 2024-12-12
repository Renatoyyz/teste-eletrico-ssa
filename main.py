import sys
from PyQt5.QtWidgets import QApplication
from Model.TelaInicial import TelaInicial
from Controller.IOs import IO_MODBUS

from Controller.Dados import Dado

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dado = Dado()
    io = IO_MODBUS()

    window = TelaInicial(io=io, dado=dado)
    window.show()
    sys.exit([app.exec(), io.ser.close()])