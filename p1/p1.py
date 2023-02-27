"""
@author: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""
import sys

from sly import Lexer

# Se proporciona LogLexer como el analizador léxico de base que debéis completar.
# Podéis implementar lexers adicionales si decidís realizar un análisis léxico condicional.

def generateDict(dictName, key):
    if key not in dictName:
        dictName[key] = 1
    else:
        dictName[key] += 1

def printDict(dictName):
    for keys, values in dictName.items():
        print(keys, ',', values, sep='')

class LogLexer(Lexer):
    '''
    Lexer base que debéis completar
    Utilizado para el análisis de la parte fija de los logs (hasta servicio)
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
        # comprobación de la quincena
        if int(t.value) < 16: 
            self.half = 'primera'
        else:
            self.half = 'segunda'

        key = self.month + ',' + self.half
        generateDict(self.dictDate, key)

        return t
    
    def MACHINE(self, t):
        # eventos por máquina
        key = str(t.value)
        generateDict(self.dictMachine, key)

        self.temp_machine = t.value

    def HOUR(self, t):
        # comprobación de la franja horaria
        hour = int(str(t.value[0]) + str(t.value[1]))
        if 8 <= hour < 16:
            self.morning += 1
        elif 16 <= hour < 24:
            self.aft += 1
        else:
            self.night += 1
        return t

    def SERVICE(self, t):
        # llamada de arranque al segundo lexer
        self.begin(MessageLexer)

    def print_output(self):
        '''
        Función encargada de mostrar el resultado final tras realizar el análisis léxico.
        Debéis implementarla como consideréis oportuno, mostrando por salida estándar los
        contadores indicados en el enunciado según el formato especificado.
        '''

        print(f'#contadores_generales\ntotal_eventos,{self.counter}\ntotal_aceptados,{self.acc}\ntotal_fallidos,{self.failed}\ntotal_no_autorizados,{self.invalid}\ntotal_otros,{self.others}')

        print('#eventos_por_fecha') 
        printDict(self.dictDate)

        print(f'#eventos_por_hora\nmanana,{self.morning}\ntarde,{self.aft}\nnoche,{self.night}') 

        print('#eventos_por_maquina') 
        printDict(self.dictMachine)

        print('#eventos_aceptados_por_maquina')
        printDict(self.dictAcc_Mach)

        print('#eventos_aceptados_por_usuario')
        printDict(self.dictAcc_User)

        print('#eventos_aceptados_por_ip') 
        printDict(self.dictAcc_IP)

        print('#eventos_fallidos_por_maquina') 
        printDict(self.dictFailed_Mach)

        print('#eventos_fallidos_por_usuario') 
        printDict(self.dictFailed_User)

        print('#eventos_fallidos_por_ip') 
        printDict(self.dictFailed_IP)

        print('#eventos_no_autorizados_por_maquina') 
        printDict(self.dictInvalid_Mach)

        print('#eventos_no_autorizados_por_usuario') 
        printDict(self.dictInvalid_User)

        print('#eventos_no_autorizados_por_ip') 
        printDict(self.dictInvalid_IP)  

class MessageLexer(Lexer):
    """
    Lexer para el análisis de la parte del mensaje de los logs   
    """

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
        # llamada de arranque al primer lexer
        self.begin(LogLexer)

    def MESSAGE(self, t):
        # Total de mensajes identificados
        if t.value == ': Accepted password for':
            self.acc += 1 
            self.temp_msg = 'accepted'

            key = self.temp_machine
            generateDict(self.dictAcc_Mach, key)

        elif t.value == ': Failed password for':
            self.failed += 1
            self.temp_msg = 'failed'

            key = self.temp_machine
            generateDict(self.dictFailed_Mach, key)
            
        else:
            self.invalid += 1
            self.temp_msg = 'invalid'

            key = self.temp_machine
            generateDict(self.dictInvalid_Mach, key)

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
                key = 'clase_a,' + 'privada'
            else:
                key = 'clase_a,' + 'publica'

        elif 127 < typeIP < 192: # tipo B
            if t.value[5] == '.':
                IP2 = int(str(t.value[4]))
            elif t.value[6] == '.':
                IP2 = int(str(t.value[4]) + str(t.value[5]))
            else:
                IP2 = int(str(t.value[4]) + str(t.value[5]) + str(t.value[6]))
                
            if typeIP == 172 and 15 < IP2 < 32:
                key = 'clase_b,' + 'privada'
            else:
                key = 'clase_b,' + 'publica'

        else: # tipo C
            if t.value[5] == '.':
                IP2 = int(str(t.value[4]))
            elif t.value[6] == '.':
                IP2 = int(str(t.value[4]) + str(t.value[5]))
            else:
                IP2 = int(str(t.value[4]) + str(t.value[5]) + str(t.value[6])) 

            if typeIP == 192 and IP2 == 168:
                key = 'clase_c,' + 'privada'
            else:
                key = 'clase_c,' + 'publica'

        if self.temp_msg == 'accepted':
            generateDict(self.dictAcc_IP, key)
        elif self.temp_msg == 'failed':
            generateDict(self.dictFailed_IP, key)
        else:
            generateDict(self.dictInvalid_IP, key)

        return t

    def USER(self, t):
        key = t.value
        if self.temp_msg == 'accepted':
            generateDict(self.dictAcc_User, key)           
        elif self.temp_msg == 'failed':
            generateDict(self.dictFailed_User, key)
        else:
            generateDict(self.dictInvalid_User, key)

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