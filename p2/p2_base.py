"""
@author: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""
import sys

from sly import Lexer, Parser


class GPXLexer(Lexer):
    TOKENS = {ELEV_OPEN, ELEV_CLOSE, HR_OPEN, HR_CLOSE, CAD_OPEN, CAD_CLOSE, 
    TEMP_OPEN, TEMP_CLOSE, NAME_OPEN, NAME_CLOSE, TYPE_OPEN, TYPE_CLOSE, LATITUDE, 
    LONGITUDE, DATE_OPEN, DATE_CLOSE, OTHERS, VALUE}

    ignore = ' \t'

    ELEV_OPEN = r'<ele>'
    ELEV_CLOSE = r'</ele>'
    HR_OPEN = r'<ns3:hr>'
    HR_CLOSE = r'</ns3:hr>'
    CAD_OPEN = r'<ns3:cad>'
    CAD_CLOSE = r'</ns3:cad>'
    TEMP_OPEN = r'<ns3:atemp>'
    TEMP_CLOSE = r'</ns3:atemp>'
    NAME_OPEN = r'<name>'
    NAME_CLOSE = r'</name>'
    TYPE_OPEN = r'<type>'
    TYPE_CLOSE = r'</type>'
    LATITUDE = r'lat="\.+"'
    LONGITUDE = r'lon="\.+"'
    DATE_OPEN = r'<time>'
    DATE_CLOSE = r'</time>'
    OTHERS = r'<.+>|<.+|.+>'
    VALUE = r'.+'
    


class GPXParser(Parser):
    tokens = GPXLexer.tokens

    # No debéis modificar el comportamiento de esta sección
if __name__ == '__main__':

    # Inicializa el Lexer y el Parser
    lexer = GPXLexer()
    parser = GPXParser()

    # Lee íntegramente el fichero proporcionado por entrada estándar
    # Windows: Get-Content example.gpx | python p2.py
    # Unix: python p2.py < example.gpx
    text = sys.stdin.read()

    tokens = None

    # Procesa los tokens (análisis léxico) y e invoca el análisis sintáctico
    # La salida (json) debe imprimirse en el axioma o (si es el caso) en la
    # función de error.
    if text:
        parser.parse(lexer.tokenize(text))
