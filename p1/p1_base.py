import sys

from sly import Lexer

# Se proporciona LogLexer como el analizador léxico de base que debéis completar.
# Podéis implementar lexers adicionales si decidís realizar un análisis léxico condicional.


class LogLexer(Lexer):
    '''
    Lexer base que debéis completar
    '''

    tokens = {MONTH, DAY, HOUR, NAME, SERVICE, REM}
    ignore = ' \t'

    # tokens separados para clase de IP

    MONTH = r'[A-Z][a-z]{2}'
    HOUR = r'[0-9]+[:][0-9]+[:][0-9]+'
    DAY = r'[0-9]{1,2}'
    SERVICE = r'sshd\[[0-9]+\]'
    NAME = r'[a-zA-Z0-9]+'
    #OTHERS = r''
    REM = r':\s.+'

    ignore_newline = r'\r?\n'

    def __init__(self):
        self.counter = 1
        self.dictDate = dict()
        self.month = ''
        self.half = ''
        self.morning = 0
        self.aft = 0
        self.night = 0
        self.acc = 0
        self.failed = 0
        self.invalid = 0
        self.tem_msg = ''
        self.dictMachine = dict()
        self.dictIP = dict()
        self.dictUser = dict()
        self.dictClass = dict()

    def ignore_newline(self, t): 
        self.counter += 1

    def MONTH(self, t):
        self.month = t.value 

    def DAY(self, t):
        if int(t.value) < 16:
            self.half = '1'
        else:
            self.half = '2'

        key = self.month + self.half

        if key not in self.dictDate:
            self.dictDate[key] = 1
        else:
            self.dictDate[key] += 1

    def HOUR(self, t):
        hour = int(str(t.value[0]) + str(t.value[1]))
        if 8 <= hour < 16:
            self.morning += 1
        elif 16 <= hour < 24:
            self.aft += 1
        else:
            self.night += 1

    def REM(self, t):
        self.begin(MessageLexer)

    def print_output(self):
        '''
        Función encargada de mostrar el resultado final tras realizar el análisis léxico.
        Debéis implementarla como consideréis oportuno, mostrando por salida estándar los
        contadores indicados en el enunciado según el formato especificado.
        '''

        print('#contadores_generales\ntotal_eventos,'f'{self.counter}')
        for keys, values in self.dictDate.items():
            print(keys, values)
        print('#eventos_por_hora\nmanana,'f'{self.morning}','\ntarde,',f'{self.aft}','\nnoche,'f'{self.night}')

class MessageLexer(Lexer):
    tokens = {MESSAGE, USER, IP}
    ignore = r' \t:'

    MESSAGE = r'Accepted\spassword\sfor|Failed\spassword\sfor\sinvalid\suser|Invalid\suser|Failed\spassword\sfor'  # e la clase secundaria
    IP = r'[0-9]+[\.][0-9]+[\.][0-9]+[\.][0-9]+'
    USER = r'[a-zA-Z0-9]+'

    def MESSAGE(self, t):
        # Total de mensajes identificados
        if t.value == 'Accepted password for':
            self.acc += 1 
            self.temp_msg = 'acc'
        elif t.value == 'Failed password for':
            self.failed += 1
            self.temp_msg = 'failed'
        else:
            self.invalid += 1
            self.temp_msg = 'invalid'

    def IP(self, t):
        # Número de eventos por máquina (total)
        k = str(t.value)
        if key not in self.dictMachine:
            self.dictMachine[k] = 1
        else:
            self.dictMachine[k] += 1

        # Número de eventos por máquina según mensaje
        key = self.temp_msg + str(t.value)
        if key not in self.dictIP:
            self.dictIP[key] = 1
        else:
            self.dictIP[key] += 1

        # Contadores según tipo de IP
        typeIP = int(str(t.value[0]) + str(t.value[1]) + str(t.value[2]))
        if typeIP < 128: # tipo A
            if str(t.value[0]) + str(t.value[1]) + str(t.value[2]) == '10.':
                key1 = self.temp_msg + 'A' + 'private'
            else:
                key1 = self.temp_msg + 'A' + 'public'
        elif 127 < typeIP < 192: # tipo B
            if int(str(t.value[0]) + str(t.value[1]) + str(t.value[2])) == 172 and 15 < int(str(t.value[4]) + str(t.value[5])) < 32:
                key1 = self.temp_msg + 'B' + 'private'
            else:
                key1 = self.temp_msg + 'B' + 'public'
        else: # tipo C
            if int(str(t.value[0]) + str(t.value[1]) + str(t.value[2])) == 192 and int(str(t.value[4]) + str(t.value[5]) + str(t.value[6])) == 168:
                key1 = self.temp_msg + 'C' + 'private'
            else:
                key1 = self.temp_msg + 'C' + 'public'

        if key1 not in self.dictClass:
            self.dictClass[key1] = 1
        else:
            self.dictClass[key1] += 1

        self.begin(LogLexer)

    def USER(self, t):
        key = self.temp_msg + str(t.value)
        if key not in self.dictUser:
            self.dictUser[key] = 1
        else:
            self.dictUser[key] += 1

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

    
    """ lexer = LogLexer()

    while True:
        try:
            text = input(' > ')
        except EOFError:
            break
        if text:
            tokens = list(lexer.tokenize(text))
            for t in tokens:
                print(t) """
