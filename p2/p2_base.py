"""
@author: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""
import sys

from sly import Lexer, Parser


class GPXLexer(Lexer):
    TOKENS = {ELEVATION, HEART_RATE, CADENCE, TEMPERATURE, NAME, TYPE, LATITUDE, LONGITUDE, DATETIME}
    ignore = ' \t\"'

    ELEVATION = r'<ele>[0-9]+</ele>'
    HEART_RATE = r'<ns3:hr>[0-9]+</ns3:hr>'
    CADENCE = r'<ns3:cad>[0-9]+</ns3:cad>'
    TEMPERATURE = r'<ns3:atemp>[0-9]+\.[0-9]+</ns3:atemp>'
    NAME = r'<name>[a-zA-Z\s]+</name>'
    TYPE = r'<type>[a-zA-Z_]+</type>'
    LATITUDE = r'lat=[0-9]+\.[0-9]+'
    LONGITUDE = r'lon=[0-9]+\.[0-9]+'
    DATETIME = r'<time>[A-Z0-9:\.-]+</time>'


class GPXParser(Parser):
    pass

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
