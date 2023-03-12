"""
@author: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""
import sys

from sly import Lexer, Parser

## Definir tokens para todas las etiquetas y no usar OTHERS
## ¿Como controlar la etiqueta que falta?

class GPXLexer(Lexer):
    TOKENS = {ELEV_OPEN, ELEV_CLOSE, HR_OPEN, HR_CLOSE, CAD_OPEN, CAD_CLOSE, TEMP_OPEN, 
    TEMP_CLOSE, NAME_OPEN, NAME_CLOSE, TYPE_OPEN, TYPE_CLOSE, LATITUDE, LONGITUDE, DATE_OPEN, 
    DATE_CLOSE, TRKSEG_OPEN, TRKSEG_CLOSE, TEXT_OPEN, TEXT_CLOSE, OTHERS, VALUE}

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
    TRKSEG_OPEN = r'<trkseg>'
    TRKSEG_CLOSE = r'</trkseg>'
    TEXT_OPEN = r'<text>'
    TEXT_CLOSE = r'</text>'
    OTHERS = r'<.+>|<.*|.*>'
    VALUE = r'.+'

    ignore_newline = r'(\r?\n)+'
    

class GPXParser(Parser):
    tokens = GPXLexer.tokens

    def __init__(self):
        self.names = {}
        self.elevation = []
        self.heart_rate = []
        self.cadence = []
        self.temperature = []

    @_('ELEV_OPEN VALUE ELEV_CLOSE')
    def elevation(self, p):
        try:
            self.elevation.append(float(p.VALUE))
            return p.VALUE
        except ValueError:
            print(f"Valor de elevación no válido ('{p.VALUE}') en la línea {self.lineno}")
    
    @_('HR_OPEN VALUE HR_CLOSE')
    def hr(self, p):
        try:
            if int(p.VALUE) <= 0:
                print(f"Valor de cadencia no válido ('{p.VALUE}') en la línea {self.lineno}")
            else:
                self.heart_rate.append(int(p.VALUE))
                return p.VALUE
        except ValueError:
            print(f"Valor de cadencia no válido ('{p.VALUE}') en la línea {self.lineno}") 

    @_('CAD_OPEN VALUE CAD_CLOSE')
    def cad(self, p):
        try:
            if int(p.VALUE) <= 0:
                print(f"Valor de cadencia no válido ('{p.VALUE}') en la línea {self.lineno}")
            else:
                self.cadence.append(int(p.VALUE))
                return p.VALUE
        except ValueError:
            print(f"Valor de cadencia no válido ('{p.VALUE}') en la línea {self.lineno}")

    @_('TEMP_OPEN VALUE TEMP_CLOSE')
    def temp(self, p):
        try:
            self.temperature.append(float(p.VALUE))
            return p.VALUE
        except ValueError:
            print(f"Valor de temperatura no válido ('{p.VALUE}') en la línea {self.lineno}")

    @_('OTHERS temp hr cad OTHERS')
    def tpe(self, p):
        return p[1], p[2], p[3]

    @_('OTHERS tpe OTHERS')
    def extensions(self, p):
        return p.tpe 

    @_('TIME_OPEN VALUE TIME_CLOSE')
    def time(self, p): ####### revisar si puede haber errores???
        return p.VALUE

    @_('OTHERS LATITUDE LONGITUDE OTHERS')
    def coords(self, p):
        return p.LATITUDE, p.LONGITUDE

    @_('coords elevation time extensions OTHERS')
    def trkpt(self, p):
        return p.coords, p.elevation, p.time, p.extensions

    @_('NAME_OPEN VALUE NAME_CLOSE')
    def name(self, p):
        return p.VALUE

    @_('TYPE_OPEN VALUE TYPE_CLOSE')
    def type(self, p):
        return p.VALUE

    @_('TRKSEG_OPEN trkpt')
    def trkseg(self, p):
        return p.trkpt
    
    @_('trkseg trkpt')
    def trkseg(self, p):
        return p.trkseg, p.trkpt
    
    @_('trkseg TRKSEG_CLOSE')
    def trkseg(self, p):
        return list(p.trkseg)

    @_('OTHERS name type trkseg OTHERS')
    def trk(self, p):
        return p.name, p.type, p.trkseg

    @_('TEXT_OPEN VALUE TEXT_CLOSE')
    def text(self, p):
        pass

    @_('OTHERS text OTHERS')
    def link(self, p):
        pass

    @_('OTHERS link time OTHERS')
    def metadata(self, p):
        pass

    @_('OTHERS metadata trk OTHERS')
    def gpx(self, p):
        return p.trk

    # funcion para manejar ausencia de etiquetas de apertura y cierre
    @_('error')
    def error(self, p):
        print(f"Error de sintaxis en la línea {self.lineno}")


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
