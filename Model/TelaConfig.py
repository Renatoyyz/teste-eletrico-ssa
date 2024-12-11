from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMetaObject
import os
import time

from View.tela_configuracao import Ui_telaConfiguracao

class TelaConfig(QDialog):
    def __init__(self, dado=None, io=None):
        super().__init__()
        self.dado = dado
        self.io = io

        self.TEMPO_TESTE = 1.5
        self.esquerda_ok = 0
        self.direita_ok = 0

        # self.lbStatusTesteEsquerdo.setStyleSheet("background-color: rgb(119, 118, 123);")
        self.COR_VERDE = "38, 162, 105"
        self.COR_CINZA = "119, 118, 123"
        self.COR_VERMELHO = "224, 27, 36"

        self.ui = Ui_telaConfiguracao()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Maximizar a janela
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btPrincipalLigaEsquerdo.clicked.connect(self.ligaPrincipalEsquerdo)
        self.ui.btPrincipalDesligaEsquerdo.clicked.connect(self.desligaPrincipalEsquerdo)
        self.ui.btPrincipalLigaDireito.clicked.connect(self.ligaPrincipalDireito)
        self.ui.btPrincipalDesligaDireito.clicked.connect(self.desligaPrincipalDireito)

        self.ui.btAgInferiorLigaEsquerdo.clicked.connect(self.ligaAgInferiorEsquerdo)
        self.ui.btAgInferiorDesligaEsquerdo.clicked.connect(self.desligaAgInferiorEsquerdo)
        self.ui.btAgInferiorLigaDireito.clicked.connect(self.ligaAgInferiorDireito)
        self.ui.btAgInferiorDesligaDireito.clicked.connect(self.desligaAgInferiorDireito)

        self.ui.btAgSuperiorLigaEsquerdo.clicked.connect(self.ligaAgSuperiorEsquerdo)
        self.ui.btAgSuperiorDesligaEsquerdo.clicked.connect(self.desligaAgSuperiorEsquerdo)
        self.ui.btAgSuperiorLigaDireito.clicked.connect(self.ligaAgSuperiorDireito)
        self.ui.btAgSuperiorDesligaDireito.clicked.connect(self.desligaAgSuperiorDireito)

        self.ui.btTesteEsquerdo.clicked.connect(self.testeEsquerdo)
        self.ui.btTesteDireito.clicked.connect(self.testeDireito)

        self.limpa_status("ambos")
    
    # Funções de controle do atuadores principais esquerdo e direito
    def ligaPrincipalEsquerdo(self):
        self.io.aciona_principal_esquerdo(1)
        self.limpa_status("esquerdo")
    
    def desligaPrincipalEsquerdo(self):
        self.io.aciona_principal_esquerdo(0)
        self.limpa_status("esquerdo")

    def ligaPrincipalDireito(self):
        self.io.aciona_principal_direito(1)
        self.limpa_status("direito")

    def desligaPrincipalDireito(self):
        self.io.aciona_principal_direito(0)
        self.limpa_status("direito")
    # Fim das funções de controle do atuadores principais

    # Funções de controle dos atuadores de agulha inferior esquerdo e direito
    def ligaAgInferiorEsquerdo(self):
        self.io.aciona_ag_inferior_esquerdo(1)
        self.limpa_status("esquerdo")

    def desligaAgInferiorEsquerdo(self):
        self.io.aciona_ag_inferior_esquerdo(0)
        self.limpa_status("esquerdo")

    def ligaAgInferiorDireito(self):
        self.io.aciona_ag_inferior_direito(1)
        self.limpa_status("direito")

    def desligaAgInferiorDireito(self):
        self.io.aciona_ag_inferior_direito(0)
        self.limpa_status("direito")
    # Fim das funções de controle dos atuadores de agulha inferior

    # Funções de controle dos atuadores de agulha superior esquerdo e direito
    def ligaAgSuperiorEsquerdo(self):
        self.io.aciona_ag_superior_esquerdo(1)
        self.limpa_status("esquerdo")

    def desligaAgSuperiorEsquerdo(self):
        self.io.aciona_ag_superior_esquerdo(0)
        self.limpa_status("esquerdo")

    def ligaAgSuperiorDireito(self):
        self.io.aciona_ag_superior_direito(1)
        self.limpa_status("direito")

    def desligaAgSuperiorDireito(self):
        self.io.aciona_ag_superior_direito(0)
        self.limpa_status("direito")
    # Fim das funções de controle dos atuadores de agulha superior
    
    def testeEsquerdo(self):
        self.io.io_rpi.aciona_leitor_eletrodo(1)
        self.limpa_status("esquerdo")
        time.sleep(self.TEMPO_TESTE)

        self.io.io_rpi.aciona_leitor_eletrodo(0)# Desliga o leitor de eletrodo
        time.sleep(0.5) # Cria um atraso

        # Verifica se o eletrodo esquerdo foi passado
        self.esquerda_ok = int(self.io.io_rpi.passa_esquerdo)

        if self.esquerda_ok == 1:
            self.ui.lbStatusTesteEsquerdo.setStyleSheet(f"background-color: rgb({self.COR_VERDE});")
        else:
            self.ui.lbStatusTesteEsquerdo.setStyleSheet(f"background-color: rgb({self.COR_VERMELHO});")

    def testeDireito(self):
        self.io.io_rpi.aciona_leitor_eletrodo(1)
        self.limpa_status("direito")
        time.sleep(self.TEMPO_TESTE)

        self.io.io_rpi.aciona_leitor_eletrodo(0)# Desliga o leitor de eletrodo
        time.sleep(0.5) # Cria um atraso

        # Verifica se o eletrodo direito foi passado
        self.direita_ok = int(self.io.io_rpi.passa_direito)

        if self.direita_ok == 1:
            self.ui.lbStatusTesteDireito.setStyleSheet(f"background-color: rgb({self.COR_VERDE});")
        else:
            self.ui.lbStatusTesteDireito.setStyleSheet(f"background-color: rgb({self.COR_VERMELHO});")

    def limpa_status(self, status):
        if status == "esquerdo":
            self.ui.lbStatusTesteEsquerdo.setStyleSheet(f"background-color: rgb({self.COR_CINZA});")
        elif status == "direito":
            self.ui.lbStatusTesteDireito.setStyleSheet(f"background-color: rgb({self.COR_CINZA});")
        elif status == "ambos":
            self.ui.lbStatusTesteEsquerdo.setStyleSheet(f"background-color: rgb({self.COR_CINZA});")
            self.ui.lbStatusTesteDireito.setStyleSheet(f"background-color: rgb({self.COR_CINZA});")

    def voltar(self):
        self.close()

    def closeEvent(self, event):
        self.ui.lbStatusTesteEsquerdo.setStyleSheet(f"background-color: rgb({self.COR_CINZA});")    
        self.ui.lbStatusTesteDireito.setStyleSheet(f"background-color: rgb({self.COR_CINZA});")
        self.io.io_rpi.aciona_leitor_eletrodo(0)# Desliga o leitor de eletrodo
        event.accept()
        