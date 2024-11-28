from machine import Pin, ADC
import time

# Configuração dos pinos do multiplexador superior (U2)
mux_pins = [Pin(10, Pin.OUT), Pin(4, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT)]
# Configuração dos pinos do multiplexador inferior (U3)
mux_pins_inferior = [Pin(5, Pin.OUT), Pin(6, Pin.OUT)]

states_curto_left = []
states_curto_right = []
state_left = []
state_right = []

start_routine = False

# Configuração do ADC
adc = Pin(20, Pin.IN, Pin.PULL_UP)#ADC(0)


# Configuração dos pinos de controle
start_pin = Pin(21, Pin.IN, Pin.PULL_UP)
output_pin_esquerdo = Pin(12, Pin.OUT)
output_pin_direito = Pin(13, Pin.OUT)

# Função para selecionar o canal dos multiplexadores a partir do canal x8
def select_channel(channel):
    channel += 8  # Ajusta o canal para começar a partir de x8

    if channel == 8:# Converte para binário o número 8
        mux_pins[0].value(0)
        mux_pins[1].value(0)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
        combina_inferior_continuidade(0)
    elif channel == 9:# Converte para binário o número 9
        mux_pins[0].value(1)
        mux_pins[1].value(0)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
        combina_inferior_continuidade(1)
    elif channel == 10:# Converte para binário o número 10
        mux_pins[0].value(0)
        mux_pins[1].value(1)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
        combina_inferior_continuidade(2)
    elif channel == 11:# Converte para binário o número 11
        mux_pins[0].value(1)
        mux_pins[1].value(1)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
        combina_inferior_continuidade(3)
    elif channel == 12:# Converte para binário o número 12
        mux_pins[0].value(0)
        mux_pins[1].value(0)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
        combina_inferior_continuidade(0)
    elif channel == 13:# Converte para binário o número 13
        mux_pins[0].value(1)
        mux_pins[1].value(0)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
        combina_inferior_continuidade(1)
    elif channel == 14:# Converte para binário o número 14
        mux_pins[0].value(0)
        mux_pins[1].value(1)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
        combina_inferior_continuidade(2)
    elif channel == 15:# Converte para binário o número 15
        mux_pins[0].value(1)
        mux_pins[1].value(1)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
        combina_inferior_continuidade(3)

def combina_inferior_continuidade(channel):

    if channel == 0:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
    elif channel == 1:
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
    elif channel == 2:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
    elif channel == 3:
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)

# Função para selecionar o canal dos multiplexadores usando arrtime.sleep(0.5)anjos
def select_channel_circuit_break(channel):
    channel += 8  # Ajusta o canal para começar a partir de x8
    # Seleciona o canal do multiplexador superior (U2)
    if channel == 8:# Converte para binário o número 8
        mux_pins[0].value(0)
        mux_pins[1].value(0)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
    elif channel == 9:# Converte para binário o número 9
        mux_pins[0].value(1)
        mux_pins[1].value(0)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
    elif channel == 10:# Converte para binário o número 10
        mux_pins[0].value(0)
        mux_pins[1].value(1)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
    elif channel == 11:# Converte para binário o número 11
        mux_pins[0].value(1)
        mux_pins[1].value(1)
        mux_pins[2].value(0)
        mux_pins[3].value(1)
    elif channel == 12:# Converte para binário o número 12
        mux_pins[0].value(0)
        mux_pins[1].value(0)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
    elif channel == 13:# Converte para binário o número 13
        mux_pins[0].value(1)
        mux_pins[1].value(0)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
    elif channel == 14:# Converte para binário o número 14
        mux_pins[0].value(0)
        mux_pins[1].value(1)
        mux_pins[2].value(1)
        mux_pins[3].value(1)
    elif channel == 15:# Converte para binário o número 15
        mux_pins[0].value(1)
        mux_pins[1].value(1)
        mux_pins[2].value(1)
        mux_pins[3].value(1)

    if channel == 8:
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)
        states_curto_left.append(adc.value())
    elif channel == 9:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)
        states_curto_left.append(adc.value())
    elif channel == 10:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)
        states_curto_left.append(adc.value())
    elif channel == 11:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
        states_curto_left.append(adc.value())
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
        states_curto_left.append(adc.value())
    elif channel == 12:
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)
        states_curto_right.append(adc.value())
    elif channel == 13:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)
        states_curto_right.append(adc.value())
    elif channel == 14:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(1)
        states_curto_right.append(adc.value())
    elif channel == 15:
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(0)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(1)
        mux_pins_inferior[1].value(0)
        states_curto_right.append(adc.value())
        mux_pins_inferior[0].value(0)
        mux_pins_inferior[1].value(1)
        states_curto_right.append(adc.value())

# Função para varrer as entradas dos multiplexadores
def scan_mux():
    states = []
    for channel in range(8):
        select_channel(channel)
        time.sleep(0.01)  # Pequena pausa para estabilizar a leitura
        states.append(adc.value())
    return states

def scan_mux_curto():
    for channel in range(8):
        select_channel_circuit_break(channel)
        time.sleep(0.01)  # Pequena pausa para estabilizar a leitura

def limpa_lista():
    states_curto_left.clear()
    states_curto_right.clear()
    state_left.clear()
    state_right.clear()

while True:
    if start_pin.value() == 0:
        time.sleep(0.1)
        if start_routine == False:
            start_routine = True
            limpa_lista()
            # Inicia a varredura
            print("Iniciando varredura...")
            states = scan_mux()
            state_left = states[:4]
            state_right = states[4:]
            scan_mux_curto() # Varre os canais de curto-circuito
    else:
        # Verifica se todas as entradas estão em 1 para continuidade e 0 para curto-circuito
        if all(state == 0 for state in state_left) and all(state == 1 for state in states_curto_left):
            output_pin_esquerdo.value(1)
            print(f"Esquerdo {states_curto_left}")
        else:
            output_pin_esquerdo.value(0)
            #limpa_lista()

        # Verifica se todas as entradas estão em 1 para continuidade e 0 para curto-circuito
        if all(state == 0 for state in state_right) and all(state == 1 for state in states_curto_right):
            output_pin_direito.value(1)
            print(f"Direito {states_curto_right}")
        else:
            output_pin_direito.value(0)
            #limpa_lista()
        print(f"Esquerdo: {state_left}")
        print(f"Esquerdo: {states_curto_left}")
        print(f"Direito: {state_right}")
        print(f"Direito: {states_curto_right}")
        
        start_routine = False
        
    time.sleep(0.5)
