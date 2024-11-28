from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread, pyqtSignal,pyqtSlot, QMetaObject, Q_ARG
import os
from datetime import datetime

from View.tela_inicial import Ui_fmTelaInicial

class Atualizador(QThread):
    sinal_atualizar = pyqtSignal(str)

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True

    def run(self):
        while self._running:
            try:
                data_hora = datetime.now()
                data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S")
                self.sinal_atualizar.emit(data_formatada)
                self.msleep(100)
            except Exception as e:
                print(f"Erro na Thread Atualizador: {e}")
                self.parar()

    def iniciar(self):
        self._running = True
        self.start()
    def parar(self):
        self._running = False

class ExecutaRotinaThread(QThread):
    sinal_execucao = pyqtSignal(int,int)# Inicializa com a quantidade de variáveis que se deseja

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True
        self.esquerda_ok =0
        self.direita_ok =0

    def run(self):
        while self._running == True:
            # Emite o sinal para atualizar a interface do usuário
            try:
                # Verifica se a rotina foi iniciada
                if self.operacao.inicia_rotina == True:
                    self.operacao.io.desaciona_pistoes()
                    self.operacao.io.aciona_matriz(1,1)# Aciona principal 1
                    self.operacao.io.aciona_matriz(2,1)# Aciona principal 2
                    self.msleep(1000) # Cria um atraso de 1 segundo
                    self.operacao.io.aciona_matriz(5,1)# Aciona AG_inferior_1
                    self.operacao.io.aciona_matriz(6,1)# Aciona AG_inferior_2
                    self.msleep(1000) # Cria um atraso de 1 segundo
                    self.operacao.io.aciona_matriz(3,1)# Aciona AG_superior_1
                    self.operacao.io.aciona_matriz(4,1)# Aciona AG_superior_2
                    self.msleep(1000) # Cria um atraso de 1 segundo
                    self.operacao.io.io_rpi.aciona_leitor_eletrodo(1)# Aciona o leitor de eletrodo
                    self.msleep(1000) # Cria um atraso de 1 segundo

                    self.operacao.io.io_rpi.aciona_leitor_eletrodo(0)# Desliga o leitor de eletrodo
                    self.msleep(1000) # Cria um atraso de 1 segundo

                    # Verifica se o eletrodo foi passado
                    self.esquerda_ok = int(self.operacao.io.io_rpi.passa_esquerdo)
                    self.direita_ok = int(self.operacao.io.io_rpi.passa_direito)

                    # Desabilita a rotina
                    self.operacao.inicia_rotina = False
                    self.operacao._acionamento_botao = 0
                    # Emite o evento para conclusão so processo
                    self.sinal_execucao.emit(self.esquerda_ok,self.direita_ok)
                    # self.sinal_execucao.emit(0,0)
                    # self.parar()
                    
                self.msleep(100)  # Cria um atraso de 100 mili segundo
            except Exception as e:
                    print(f"Erro na Thread ExecutaRotina: {e}")
                    self.parar()
    def iniciar(self):
        self._running = True
        self.start()
    def parar(self):
        self._running = False

class TelaInicial(QMainWindow):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()

        self.io = io
        self.dado = dado
        self.database = db
        self.dado.set_telas(self.dado.TELA_INICIAL)
        self.rotina = rotina

        self.inicia_rotina = False
        self._acionamento_botao = 0
        self.pecas_aprovadas = 0
        self.pecas_reprovadas = 0

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_fmTelaInicial()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Maximizar a janela
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.mouseReleaseEvent = self.setfoccus

        self.inicializa_threads()

    def inicializa_threads(self):
        # Atualizador Thread
        self.atualizador = Atualizador(self)
        self.atualizador.sinal_atualizar.connect(self.thread_atualizar_valor)
        self.atualizador.iniciar()

        # ExecutaRotinaThread
        self.execucao_ = ExecutaRotinaThread(self)
        self.execucao_.sinal_execucao.connect(self.thread_execucao)
        self.execucao_.iniciar()

        QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
    
    def thread_atualizar_valor(self, data_hora):
        QMetaObject.invokeMethod(self, "atualiza_valor", Qt.QueuedConnection, Q_ARG(str, data_hora))

    @pyqtSlot(str)
    def atualiza_valor(self, data_hora):
        if self.io.io_rpi.bot_acio_e == 0 and self.io.io_rpi.bot_acio_d == 0:
            if self._acionamento_botao < 1:
                self.inicia_rotina = True # Inicia a rotina de teste
                self._acionamento_botao += 1 # Incrementa a variável para evitar que a rotina seja iniciada mais de uma vez

    def thread_execucao(self, esquerda, direita):
        QMetaObject.invokeMethod(self, "execucao", Qt.QueuedConnection, 
                                 Q_ARG(int, esquerda), Q_ARG(int, direita))

    @pyqtSlot(int, int)
    def execucao(self,  esquerda, direita):
        if esquerda == 1 and direita == 1:
            self.ui.lbPecasAprovadas.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:24pt; font-weight:600;\">{esquerda}</span></p></body></html>")
            self.ui.lbPecasReprovadas.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:24pt; font-weight:600;\">{direita}</span></p></body></html>")

    def desligar_sistema(self):
        self.shutdown_pi()
        self.close()

    def shutdown_pi(self):
        print("Desligando o Raspberry Pi com segurança...")
        QThread.sleep(10)
        os.system("sudo shutdown now")


    def closeEvent(self, event):
        event.accept()

    def setfoccus(self, event):
        if self.io.io_rpi.bot_acio_d == 0:
            self.close()