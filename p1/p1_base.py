import sys

from sly import Lexer

# Se proporciona LogLexer como el analizador léxico de base que debéis completar.
# Podéis implementar lexers adicionales si decidís realizar un análisis léxico condicional.


class LogLexer(Lexer):
    '''
    Lexer base que debéis completar
    '''

    tokens = {FECHA, NOMBRE, SERVICIO, MENSAJE}

    FECHA = r'[a-zA-Z]+[ |\t][0-9]+[ |\t][0-9:]+' ## revisar espacios en blanco --> \s 
    NOMBRE = r'[a-zA-Z0-9]+'
    SERVICIO = r'sshd\[[0-9]+\]'
    MENSAJE = r'Accepted password for|Failed password for|Invalid user|Failed password for invalid user' # gestionar demas tipos de eventos
    # añadir mas tokens para el resto de campos del mensaje

    ##################
    # ¿¿¿¿¿Será util análisis lexico condicional para gestionar todas las partes del mensaje????????????????
    ##################


    ignore = r': ' # que ignore los dos puntos del campo ssh
    ignore_space = r' '
    ignore_newline = r'\r?\n'

    def __init__(self):
        self.contador = 1 # inicializado a 1 porque el nº de eventos es igual al nº de saltos de linea + 1

    def ignore_newline(self, t): # se puede utilizar para contador del numero total de eventos? sumando 1 al final porque hay un salto de linea menos que numero de eventos
        self.contador += 1

    def print_output(self):
        '''
        Función encargada de mostrar el resultado final tras realizar el análisis léxico.
        Debéis implementarla como consideréis oportuno, mostrando por salida estándar los
        contadores indicados en el enunciado según el formato especificado.
        '''

        print('#contadores_generales\ntotal_eventos,'f'{self.contador}')


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
