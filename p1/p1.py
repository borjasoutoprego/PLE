"""
@author: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""
import sys

from sly import Lexer

# Se proporciona LogLexer como el analizador léxico de base que debéis completar.
# Podéis implementar lexers adicionales si decidís realizar un análisis léxico condicional.


class LogLexer(Lexer):
    '''
    Lexer base que debéis completar
    '''

    tokens = {MONTH, DAY, HOUR, MACHINE, SERVICE}
    ignore = ' \t:'

    MONTH = r'[A-Z][a-z]{2}'
    HOUR = r'[0-9]+[:][0-9]+[:][0-9]+'
    DAY = r'[0-9]{1,2}'
    SERVICE = r'sshd\[[0-9]+\]'
    MACHINE = r'[a-zA-Z0-9]+'

    ignore_newline = r'\r?\n'

    def __init__(self):
        self.counter = 0
        self.dictDate = dict()
        self.month = ''
        self.half = ''
        self.morning = 0
        self.aft = 0
        self.night = 0
        self.acc = 0
        self.failed = 0
        self.invalid = 0
        self.temp_msg = ''
        self.temp_machine = ''
        self.dictMachine = dict()
        self.dictAcc_Mach = dict()
        self.dictFailed_Mach = dict()
        self.dictInvalid_Mach = dict()
        self.dictAcc_User = dict()
        self.dictFailed_User = dict()
        self.dictInvalid_User = dict()
        self.dictUser = dict()
        self.dictAcc_IP = dict()
        self.dictFailed_IP = dict()
        self.dictInvalid_IP = dict()
        self.others = 0

    def MONTH(self, t):
        self.month = t.value 
        self.counter += 1
        return t 

    def DAY(self, t):
        if int(t.value) < 16:
            self.half = 'primera'
        else:
            self.half = 'segunda'

        key = self.month + ',' + self.half

        if key not in self.dictDate:
            self.dictDate[key] = 1
        else:
            self.dictDate[key] += 1

        return t
    
    def MACHINE(self, t):
        # Eventos por máquina
        k = str(t.value)
        if k not in self.dictMachine:
            self.dictMachine[k] = 1
        else:
            self.dictMachine[k] += 1

        self.temp_machine = t.value

    def HOUR(self, t):
        hour = int(str(t.value[0]) + str(t.value[1]))
        if 8 <= hour < 16:
            self.morning += 1
        elif 16 <= hour < 24:
            self.aft += 1
        else:
            self.night += 1
        return t

    def SERVICE(self, t):
        self.begin(MessageLexer)

    def print_output(self):
        '''
        Función encargada de mostrar el resultado final tras realizar el análisis léxico.
        Debéis implementarla como consideréis oportuno, mostrando por salida estándar los
        contadores indicados en el enunciado según el formato especificado.
        '''

        print(f'#contadores_generales\ntotal_eventos,{self.counter}\ntotal_aceptados,{self.acc}\ntotal_fallidos,{self.failed}\ntotal_no_autorizados,{self.invalid}\ntotal_otros,{self.others}')

        print('#eventos_por_fecha') 
        for keys, values in self.dictDate.items():
            print(keys, ',', values, sep='')

        print(f'#eventos_por_hora\nmanana,{self.morning}\ntarde,{self.aft}\nnoche,{self.night}') 

        print('#eventos_por_maquina') 
        for keys, values in self.dictMachine.items():
            print(keys, ',', values, sep='')

        print('#eventos_aceptados_por_maquina')
        for keys, values in self.dictAcc_Mach.items():
            print(keys, ',', values, sep='')

        print('#eventos_aceptados_por_usuario')
        for keys, values in self.dictAcc_User.items():
            print(keys, ',', values, sep='')

        print('#eventos_aceptados_por_ip') 
        for keys, values in self.dictAcc_IP.items():
             print(keys, ',', values, sep='')

        print('#eventos_fallidos_por_maquina') 
        for keys, values in self.dictFailed_Mach.items():
            print(keys, ',', values, sep='')

        print('#eventos_fallidos_por_usuario') 
        for keys, values in self.dictFailed_User.items():
             print(keys, ',', values, sep='')

        print('#eventos_fallidos_por_ip') 
        for keys, values in self.dictFailed_IP.items():
              print(keys, ',', values, sep='')

        print('#eventos_no_autorizados_por_maquina') 
        for keys, values in self.dictInvalid_Mach.items():
            print(keys, ',', values, sep='')

        print('#eventos_no_autorizados_por_usuario') 
        for keys, values in self.dictInvalid_User.items():
             print(keys, ',', values, sep='')

        print('#eventos_no_autorizados_por_ip') 
        for keys, values in self.dictInvalid_IP.items():
             print(keys, ',', values, sep='')     

class MessageLexer(Lexer):
    tokens = {MESSAGE, OTHERS, USER, IP, END, FROM, NEWLINE}
    ignore = r' \t'

    FROM = r'from'
    MESSAGE = r'(?i):\s(Accepted\spassword\sfor|Failed\spassword\sfor\sinvalid\suser|Invalid\suser|Failed\spassword\sfor)\b'  
    OTHERS = r':\s.+'
    IP = r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    NEWLINE = r'\r?\n'
    END =   r'port.+'
    USER = r'[^ \t]+'

    def NEWLINE(self, t):
        self.begin(LogLexer)

    def MESSAGE(self, t):
        # Total de mensajes identificados
        if t.value == ': Accepted password for':
            self.acc += 1 
            self.temp_msg = 'accepted'

            key = self.temp_machine
            if key not in self.dictAcc_Mach:
                self.dictAcc_Mach[key] = 1
            else:
                self.dictAcc_Mach[key] += 1
            
        elif t.value == ': Failed password for':
            self.failed += 1
            self.temp_msg = 'failed'

            key = self.temp_machine
            if key not in self.dictFailed_Mach:
                self.dictFailed_Mach[key] = 1
            else:
                self.dictFailed_Mach[key] += 1
        else:
            self.invalid += 1
            self.temp_msg = 'invalid'

            key = self.temp_machine
            if key not in self.dictInvalid_Mach:
                self.dictInvalid_Mach[key] = 1
            else:
                self.dictInvalid_Mach[key] += 1

        return t 

    def OTHERS(self, t):
        self.others += 1
        return t

    def IP(self, t):
        # Contadores según tipo de IP
        if t.value[1] == '.':
            typeIP = int(str(t.value[0]))
        elif t.value[2] == '.':
            typeIP = int(str(t.value[0]) + str(t.value[1]))
        else:
            typeIP = int(str(t.value[0]) + str(t.value[1]) + str(t.value[2]))

        if typeIP < 128: # tipo A
            if typeIP == 10:
                key1 = 'clase_a,' + 'privada'
            else:
                key1 = 'clase_a,' + 'publica'

        elif 127 < typeIP < 192: # tipo B
            if t.value[5] == '.':
                IP2 = int(str(t.value[4]))
            elif t.value[6] == '.':
                IP2 = int(str(t.value[4]) + str(t.value[5]))
            else:
                IP2 = int(str(t.value[4]) + str(t.value[5]) + str(t.value[6]))
                
            if typeIP == 172 and 15 < IP2 < 32:
                key1 = 'clase_b,' + 'privada'
            else:
                key1 = 'clase_b,' + 'publica'

        else: # tipo C
            if t.value[5] == '.':
                IP2 = int(str(t.value[4]))
            elif t.value[6] == '.':
                IP2 = int(str(t.value[4]) + str(t.value[5]))
            else:
                IP2 = int(str(t.value[4]) + str(t.value[5]) + str(t.value[6])) 

            if typeIP == 192 and IP2 == 168:
                key1 = 'clase_c,' + 'privada'
            else:
                key1 = 'clase_c,' + 'publica'

        if self.temp_msg == 'accepted':
            if key1 not in self.dictAcc_IP:
                self.dictAcc_IP[key1] = 1
            else:
                self.dictAcc_IP[key1] += 1
        elif self.temp_msg == 'failed':
            if key1 not in self.dictFailed_IP:
                self.dictFailed_IP[key1] = 1
            else:
                self.dictFailed_IP[key1] += 1
        else:
            if key1 not in self.dictInvalid_IP:
                self.dictInvalid_IP[key1] = 1
            else:
                self.dictInvalid_IP[key1] += 1

        return t

    def USER(self, t):
        key = t.value

        if self.temp_msg == 'accepted':
            if key not in self.dictAcc_User:
                self.dictAcc_User[key] = 1
            else:
                self.dictAcc_User[key] += 1
            
        elif self.temp_msg == 'failed':
            if key not in self.dictFailed_User:
                self.dictFailed_User[key] = 1
            else:
                self.dictFailed_User[key] += 1
        else:
            if key not in self.dictInvalid_User:
                self.dictInvalid_User[key] = 1
            else:
                self.dictInvalid_User[key] += 1

# No debéis modificar el comportamiento de esta sección
if __name__ == '__main__':

    # Inicializa el Lexer principal.
    lexer = LogLexer()

    # Lee íntegramente el fichero proporcionado por entrada estándar
    # Windows: Get-Content auth_example.log | python p1.py
    # Unix: python p1.py < auth_example.log
    text = sys.stdin.read()

    tokens = None

    # Procesa los tokens (análisis léxico) y e invoca la función que muestra la salida
    if text:
        list(lexer.tokenize(text, lineno=0))
        lexer.print_output()