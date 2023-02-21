import sys

from sly import Lexer

# Se proporciona LogLexer como el analizador léxico de base que debéis completar.
# Podéis implementar lexers adicionales si decidís realizar un análisis léxico condicional.


class LogLexer(Lexer):
    '''
    Lexer base que debéis completar
    '''

    tokens = {MONTH, DAY, HOUR, NAME, SERVICE, MESSAGE, OTHERS}
    ignore = ' \t:'

    MESSAGE = r'Accepted\spassword\sfor|Failed\spassword\sfor\sinvalid\suser|Invalid\suser|Failed\spassword\sfor' 
    MONTH = r'[A-Z][a-z]{2}'
    HOUR = r'[0-9]+[:][0-9]+[:][0-9]+'
    DAY = r'[0-9]{1,2}'
    SERVICE = r'sshd\[[0-9]+\]'
    NAME = r'[a-zA-Z0-9]+'
    OTHERS = r'.+'

    ignore_newline = r'\r?\n'

    def __init__(self):
        self.counter = 1 

    def ignore_newline(self, t): 
        self.counter += 1

    def MONTH(self, t):
        pass

    def DAY(self, t):
        pass

    def print_output(self):
        '''
        Función encargada de mostrar el resultado final tras realizar el análisis léxico.
        Debéis implementarla como consideréis oportuno, mostrando por salida estándar los
        contadores indicados en el enunciado según el formato especificado.
        '''

        print('#contadores_generales\ntotal_eventos,'f'{self.counter}')

#class MessageLexer(Lexer):
    #tokens = {MESSAGE, USER, IP, PORT}


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
                print(t)
 """