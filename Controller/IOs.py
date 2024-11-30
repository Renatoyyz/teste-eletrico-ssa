import serial
import time
import random

class FakeRPiGPIO:
    BCM = "BCM"
    PUD_UP = "PUD_UP"
    IN = "IN"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.pins = {}

    def setmode(self, mode):
        self.mode = mode

    def setwarnings(self, state):
        self.warnings = state

    def setup(self, pin, direction, pull_up_down=None):
        self.pins[pin] = {'direction': direction, 'state': self.HIGH if pull_up_down == self.PUD_UP else self.LOW}

    def input(self, pin):
        if pin in self.pins:
            return self.pins[pin]['state']
        raise ValueError(f"Pin {pin} not set up.")

    def output(self, pin, state):
        if pin in self.pins and self.pins[pin]['direction'] == self.OUT:
            self.pins[pin]['state'] = state
        else:
            raise ValueError(f"Pin {pin} not set up or not set as output.")

    def cleanup(self):
        self.pins.clear()


class InOut:
    def __init__(self):
        self.CORTINA_LUZ = 2
        self.SENSOR_DESCARTE = 3
        self.BOT_ACIO_E = 10
        self.BOT_ACIO_D = 24

        self.PASSA_ESQUERDO = 23
        self.PASSA_DIREITO = 22

        self.LEITOR_ELETRODO = 12


        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
        except ImportError:
            print("RPi.GPIO not found. Using fake GPIO.")
            self.GPIO = FakeRPiGPIO()

        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        
        self.GPIO.setup(self.CORTINA_LUZ, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.SENSOR_DESCARTE, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.BOT_ACIO_E, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.BOT_ACIO_D, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.PASSA_ESQUERDO, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.PASSA_DIREITO, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)

        self.GPIO.setup(self.LEITOR_ELETRODO, self.GPIO.OUT)
        self.aciona_leitor_eletrodo(0) # Inicializa o leitor de eletrodo como desativado

    @property
    def contina_luz(self):
        return self.GPIO.input(self.CORTINA_LUZ)
    
    @property
    def sensor_descarte(self):
        return self.GPIO.input(self.SENSOR_DESCARTE)

    @property
    # off_app
    def bot_acio_e(self):
        return self.GPIO.input(self.BOT_ACIO_E)

    @property
    def bot_acio_d(self):
        return self.GPIO.input(self.BOT_ACIO_D)
    
    @property
    def passa_esquerdo(self):
        return self.GPIO.input(self.PASSA_ESQUERDO)
    
    @property
    def passa_direito(self):
        return self.GPIO.input(self.PASSA_DIREITO)
    
    def aciona_leitor_eletrodo(self, state):
        state = not state
        self.GPIO.output(self.LEITOR_ELETRODO, state)
        
class IO_MODBUS:
    def __init__(self):

        self.io_rpi = InOut()

        self.fake_modbus = False
        try:
            self.ser = serial.Serial(
                                        port='/dev/ttyUSB0',  # Porta serial padrão no Raspberry Pi 4
                                        # port='/dev/tty.URT0',  # Porta serial padrão no Raspberry Pi 4
                                        baudrate=9600,       # Taxa de baud
                                        bytesize=8,
                                        parity="N",
                                        stopbits=1,
                                        timeout=1,            # Timeout de leitura
                                        #xonxoff=False,         # Controle de fluxo por software (XON/XOFF)
                                        #rtscts=True
                                    )
        except Exception as e:
            print(f"Erro ao conectar com a serial: {e}")
            return

    def crc16_modbus(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if (crc & 0x0001):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    
    def R413D08_out(self,id = 1, out=1, value=1):
        
        dados_recebidos = None

        id_loc = hex(id)[2:]
        id_loc = id_loc.zfill(2).upper()

        out_loc = hex(out)[2:]
        out_loc = out_loc.zfill(4).upper()

        if value == 1:
            hex_text = f"{id_loc} 06 {out_loc} 01 00"
        elif value == 0:
            hex_text = f"{id_loc} 06 {out_loc} 02 00"
        bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa

        crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

        parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
        parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

        id_loc = id

        try:
            if value == 1:
                self.ser.write([id_loc,0x06,0,out,1,0,parte_inferior,parte_superior])
            elif value == 0:
                self.ser.write([id_loc,0x06,0,out,2,0,parte_inferior,parte_superior])

            while self.ser.readable()==False:
                pass
            dados_recebidos = self.ser.read(8)
            dados_recebidos = dados_recebidos.hex()
            hex_text = dados_recebidos[0:2]+dados_recebidos[2:4]+dados_recebidos[4:6]+dados_recebidos[6:8]+dados_recebidos[8:10]+dados_recebidos[10:12]
            bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa
            crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

            parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
            parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

            superior_crc = int(dados_recebidos[14:16],16) # Transforma de hexa para int
            inferior_crc = int(dados_recebidos[12:14],16) # Transforma de hexa para int

            if parte_superior == superior_crc and parte_inferior == inferior_crc:
                dados_recebidos = dados_recebidos[0:2]
                dados_recebidos = int(dados_recebidos)
                # time.sleep(0.5)
                return dados_recebidos
            else:
                return -1
        except:
            return -1 # Indica erro de alguma natureza....
        
    def aciona_matriz(self,out,value):

        if out == 1:
            return self.R413D08_out(id=1,out=8,value=value)
        elif out == 2:
            return self.R413D08_out(id=2,out=8,value=value)
        elif out == 3:
            return self.R413D08_out(id=1,out=7,value=value)
        elif out == 4:
            return self.R413D08_out(id=2,out=7,value=value)
        elif out == 5:
            return self.R413D08_out(id=1,out=6,value=value)
        elif out == 6:
            return self.R413D08_out(id=2,out=6,value=value)
        elif out == 7:
            return self.R413D08_out(id=1,out=5,value=value)
        elif out == 8:
            return self.R413D08_out(id=2,out=5,value=value)
        elif out == 9:
            return self.R413D08_out(id=1,out=4,value=value)
        elif out == 10:
            return self.R413D08_out(id=2,out=4,value=value)
        elif out == 11:
            return self.R413D08_out(id=1,out=3,value=value)
        elif out == 12:
            return self.R413D08_out(id=2,out=3,value=value)
        elif out == 13:
            return self.R413D08_out(id=1,out=2,value=value)
        elif out == 14:
            return self.R413D08_out(id=2,out=2,value=value)
        elif out == 15:
            return self.R413D08_out(id=1,out=1,value=value)
        elif out == 16:
            return self.R413D08_out(id=2,out=1,value=value)
    def limpa_matriz(self):
        for i in range(1,17):
            self.aciona_matriz(i,0)

    def desaciona_pistoes(self):
        # Agulhas inferiores
        self.aciona_matriz(5,0)
        self.aciona_matriz(6,0)
        time.sleep(0.5)
        # Agulhas superiores
        self.aciona_matriz(3,0)
        self.aciona_matriz(4,0)
        time.sleep(0.5)
        # Principais
        self.aciona_matriz(1,0)
        self.aciona_matriz(2,0)
        time.sleep(0.5)

    def desaciona_pistoes_esquerdo(self):
        # Agulhas inferiores
        self.aciona_matriz(5,0)
        time.sleep(0.5)
        # Agulhas superiores
        self.aciona_matriz(3,0)
        time.sleep(0.5)
        # Principais
        self.aciona_matriz(1,0)
        time.sleep(0.5)

    def desaciona_pistoes_direito(self):
        # Agulhas inferiores
        self.aciona_matriz(6,0)
        time.sleep(0.5)
        # Agulhas superiores
        self.aciona_matriz(4,0)
        time.sleep(0.5)
        # Principais
        self.aciona_matriz(2,0)
        time.sleep(0.5)

    def passa_nao_passa_esquerdo(self, value):
        if value == 1:
            self.aciona_matriz(13,0)
            self.aciona_matriz(15,1)
        elif value == 0:
            self.aciona_matriz(15,0)
            self.aciona_matriz(13,1)
        else:
            return -1
        
    def passa_nao_passa_direito(self, value):
        if value == 1:
            self.aciona_matriz(14,0)
            self.aciona_matriz(16,1)
        elif value == 0:
            self.aciona_matriz(16,0)
            self.aciona_matriz(14,1)
        else:
            return -1
        
    def apaga_pasa_nao_passa(self):
        self.aciona_matriz(13,0)
        self.aciona_matriz(14,0)
        self.aciona_matriz(15,0)
        self.aciona_matriz(16,0)

    def aciona_marcacao_esquerdo(self):
        self.aciona_matriz(10,1)
        time.sleep(1)  
        self.aciona_matriz(12,1)  
        time.sleep(0.5)
        self.aciona_matriz(12,0)
        time.sleep(0.2)
        self.aciona_matriz(10,0) 
    
    def aciona_marcacao_direito(self):
        self.aciona_matriz(9,1)
        time.sleep(1)  
        self.aciona_matriz(11,1)  
        time.sleep(0.5)
        self.aciona_matriz(11,0)
        time.sleep(0.2)
        self.aciona_matriz(9,0)

    def aciona_principal(self, value):
        if value ==1:
            self.aciona_matriz(1,1)# Aciona principal 1
            self.aciona_matriz(2,1)# Aciona principal 2
        elif value == 0:
            self.aciona_matriz(1,0)
            self.aciona_matriz(2,0)

    def aciona_ag_inferior_esquerdo(self, value):
        if value == 1:
            self.aciona_matriz(5,1)# Aciona AG_inferior_1
            # self.aciona_matriz(6,1)# Aciona AG_inferior_2
        elif value == 0:
            self.aciona_matriz(5,0)
            # self.aciona_matriz(6,0)

    def aciona_ag_inferior_direito(self, value):
        if value == 1:
            # self.aciona_matriz(5,1)# Aciona AG_inferior_1
            self.aciona_matriz(6,1)
        elif value == 0:
            # self.aciona_matriz(5,0)
            self.aciona_matriz(6,0)

    def aciona_ag_superior(self, value):
        if value == 1:
            self.aciona_matriz(3,1)# Aciona AG_superior_1
            self.aciona_matriz(4,1)# Aciona AG_superior_2
        elif value == 0:
            self.aciona_matriz(3,0)
            self.aciona_matriz(4,0)
    
    def reset_serial(self):
        try:
            self.ser.close()
            time.sleep(0.5)  # Aguarda um curto período antes de reabrir a porta
            self.ser.open()
            self.ser.flushInput()  # Limpa o buffer de entrada após reabrir a porta
            print("Porta serial resetada com sucesso.")
        except Exception as e:
            print(f"Erro ao resetar a porta serial: {e}")

if __name__ == '__main__':
    import time
    io = IO_MODBUS()

    out = 0
    value = 0
    input_ = 0

    # while input_ !="q" and input_ !="Q":
    #     input_ = input("Digite:\n1 para acionar a matriz.\n2 para limpar a matriz.\nq para sair.\n")
    #     if input_ == "1":
    #         print("Digite o número do out (1-16):")
    #         out = int(input())
    #         print("Digite o valor (0 ou 1):")
    #         value = int(input())
    #         print(f"Acionando out {out} com valor {value}")
    #         print(f"Retorno: {io.aciona_matriz(out,value)}")
    #     elif input_ == "2":
    #         io.limpa_matriz()
    #         print("Matriz limpa.")
    #         time.sleep(1)
    while input_ !="q" and input_ !="Q":
        input_ = input("Digite:\n1 para acionar o pistão principal.\n2 para acionar a agulha inferior esquerdo.\n3 para acionar a agulha inferior direito.\n4 para acionar a agulha superior.\n5 para acionar a marcação esquerdo.\n6 para acionar a marcação direito.\nq para sair.\n")
        if input_ == "1":
            print("Pistão principal 1=liga 0=desliga")
            out = int(input())
            io.aciona_principal(out)
        elif input_ == "2":
            print("Agulha inferior esquedo 1=liga 0=desliga")
            out = int(input())
            io.aciona_ag_inferior_esquerdo(out)
        elif input_ == "3":
            print("Agulha inferior direito 1=liga 0=desliga")
            out = int(input())
            io.aciona_ag_inferior_direito(out)
        elif input_ == "4":
            print("Agulha superior 1=liga 0=desliga")
            out = int(input())
            io.aciona_ag_superior(out)
        elif input_ == "5":
            print("Aciona marcação esquerdo")
            io.aciona_marcacao_esquerdo()
        elif input_ == "6":
            print("Aciona marcação direito")
            io.aciona_marcacao_direito()
            