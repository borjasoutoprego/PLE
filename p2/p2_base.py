"""
@author: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""
import sys
import json
from sly import Lexer, Parser

## Definir tokens para todas las etiquetas y no usar OTHERS
## ¿Como controlar la etiqueta que falta?

class GPXLexer(Lexer):
    tokens = {GPX_OPEN, GPX_CLOSE, TRK_OPEN, TRK_CLOSE, ELEV_OPEN, ELEV_CLOSE, HR_OPEN, HR_CLOSE, CAD_OPEN, CAD_CLOSE, TEMP_OPEN, 
    TEMP_CLOSE, NAME_OPEN, NAME_CLOSE, TYPE_OPEN, TYPE_CLOSE, TIME_OPEN, 
    TIME_CLOSE, EXTENSIONS_OPEN, EXTENSIONS_CLOSE, TPE_OPEN, TPE_CLOSE, TRKSEG_OPEN, TRKSEG_CLOSE, 
    TRKPT_OPEN, TRKPT_CLOSE, DATE, FLOAT, INT, NEGATIVE_NUMBER, STRING}

    ignore = ' \t'
    ignore_newline = r'\r?\n'
    ignore_header = r'<\?xml.*?\?>'

    #HEADER = r'<\?xml.*?\?>'
    GPX_OPEN = r'<gpx(.|\s)*?>'
    ignore_metadata = '<metadata>([\t?\n].*?)+</metadata>'
    GPX_CLOSE = r'</gpx>'
    TRK_OPEN = r'<trk>'
    TRK_CLOSE = r'</trk>'
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
    TIME_OPEN = r'<time>'
    TIME_CLOSE = r'</time>'
    EXTENSIONS_OPEN = r'<extensions>'
    EXTENSIONS_CLOSE = r'</extensions>'
    TPE_OPEN = r'<ns3:TrackPointExtension>'
    TPE_CLOSE = r'</ns3:TrackPointExtension>'
    TRKSEG_OPEN = r'<trkseg>'
    TRKSEG_CLOSE = r'</trkseg>'
    TRKPT_OPEN = r'<trkpt.+?>'
    TRKPT_CLOSE = r'</trkpt>'
    DATE = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z'
    FLOAT = r'\d+\.\d+'
    INT = r'\d+'
    NEGATIVE_NUMBER = r'-\d+\.*\d*'
    STRING = r'[a-zA-Z_]+\s*[a-zA-Z_]*'

    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    def INT(self, t):
        t.value = int(t.value)
        return t

    def STRING(self, t):
        t.value = str(t.value)
        return t

    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        t.type = 'error'
        t.value = t.value[0]
        self.index += 1
        return t
    
class GPXParser(Parser):
    tokens = GPXLexer.tokens

    def __init__(self):
        self.elevation = []
        self.heart_rate = []
        self.cadence = []
        self.temperature = []
        # self.elevation = {'count': 0, 'min': 0, 'max': 0, 'sum': 0}
        # self.heart_rate = {'count': 0, 'min': 0, 'max': 0, 'sum': 0}
        # self.cadence = {'count': 0, 'min': 0, 'max': 0, 'sum': 0}
        # self.temperature = {'count': 0, 'min': 0, 'max': 0, 'sum': 0}
        
    @_('GPX_OPEN TRK_OPEN trk_content TRK_CLOSE GPX_CLOSE')
    def gpx(self, p):
        return p.trk_content

    @_('error TRK_OPEN trk_content TRK_CLOSE GPX_CLOSE')
    def gpx(self, p):
        print('Error: Falta la etiqueta de apertura de </gpx>')
        return p.trk_content

    @_('GPX_OPEN TRK_OPEN trk_content TRK_CLOSE error')
    def gpx(self, p):
        print('Error: Falta la etiqueta de cierre de <gpx>')
        return p.trk_content

    @_('GPX_OPEN error trk_content TRK_CLOSE GPX_CLOSE')
    def gpx(self, p):
        print('Error: Falta la etiqueta de apertura de </trk>')
        return p.trk_content

    @_('GPX_OPEN TRK_OPEN trk_content error GPX_CLOSE')
    def gpx(self, p):
        print('Error: Falta la etiqueta de cierre de <trk>')
        return p.trk_content

    @_('trk_content trk_item')
    def trk_content(self, p):
        p.trk_content.append(p.trk_item)
        return p.trk_content

    @_('trk_item')
    def trk_content(self, p):
        return [p.trk_item]

    @_('NAME_OPEN STRING NAME_CLOSE')
    def trk_item(self, p):
        return p.STRING

    @_('NAME_OPEN STRING error')
    def trk_item(self, p):
        print('Error: Falta la etiqueta de cierre de <name>')
        return p.STRING

    @_('error STRING NAME_CLOSE')
    def trk_item(self, p):
        print('Error: Falta la etiqueta de apertura de </name>')
        return p.STRING

    @_('NAME_OPEN error NAME_CLOSE')
    def trk_item(self, p):
        print(f"Valor de name no válido ('{p.error.value}') en la línea {p.error.lineno}")

    @_('TYPE_OPEN STRING TYPE_CLOSE')
    def trk_item(self, p):
        return p.STRING

    @_('error STRING TYPE_CLOSE')
    def trk_item(self, p):
        print('Error: Falta la etiqueta de apertura de </type>')
        return p.STRING

    @_('TYPE_OPEN STRING error')
    def trk_item(self, p):
        print('Error: Falta la etiqueta de cierre de <type>')
        return p.STRING

    @_('TYPE_OPEN error TYPE_CLOSE')
    def trk_item(self, p):
        print(f"Valor de type no válido ('{p.error.value}') en la línea {p.error.lineno}")

    @_('TRKSEG_OPEN trkpoints TRKSEG_CLOSE')
    def trk_item(self, p):
        return p.trkpoints

    @_('error trkpoints TRKSEG_CLOSE')
    def trk_item(self, p):
        print('Error: Falta la etiqueta de apertura de </trkseg>')
        return p.trkpoints

    @_('TRKSEG_OPEN trkpoints error')
    def trk_item(self, p):
        print('Error: Falta la etiqueta de cierre de <trkseg>')
        return p.trkpoints

    @_('trkpoints trkpt')
    def trkpoints(self, p):
        p.trkpoints.append(p.trkpt)
        return p.trkpoints

    @_('trkpt')
    def trkpoints(self, p):
        return [p.trkpt]

    @_('TRKPT_OPEN trkpt_content TRKPT_CLOSE')
    def trkpt(self, p):
        coords = p.TRKPT_OPEN.split('"')
        p.trkpt_content.append(coords[1])
        p.trkpt_content.append(coords[3])
        return p.trkpt_content 

    @_('error trkpt_content TRKPT_CLOSE')
    def trkpt(self, p):
        coords = p.TRKPT_OPEN.split('"')
        p.trkpt_content.append(coords[1])
        p.trkpt_content.append(coords[3])
        print('Error: Falta la etiqueta de apertura de </trkpt>')
        return p.trkpt_content 

    @_('TRKPT_OPEN trkpt_content error')
    def trkpt(self, p):
        coords = p.TRKPT_OPEN.split('"')
        p.trkpt_content.append(coords[1])
        p.trkpt_content.append(coords[3])
        print('Error: Falta la etiqueta de cierre de <trkpt>')
        return p.trkpt_content 

    @_('trkpt_content trkpt_item')
    def trkpt_content(self, p):
        p.trkpt_content.append(p.trkpt_item)
        return p.trkpt_content

    @_('trkpt_item')
    def trkpt_content(self, p):
        return [p.trkpt_item]

    @_('ELEV_OPEN FLOAT ELEV_CLOSE')
    def trkpt_item(self, p):
        self.elevation.append(p.FLOAT)
        return p.FLOAT

    @_('ELEV_OPEN INT ELEV_CLOSE')
    def trkpt_item(self, p):
        self.elevation.append(p.INT)
        return p.INT

    @_('ELEV_OPEN error ELEV_CLOSE')
    def trkpt_item(self, p):
        print(f"Valor de elevación no válido ('{p.error.value}') en la línea {p.error.lineno}")

    @_('TIME_OPEN DATE TIME_CLOSE')
    def trkpt_item(self, p):
        return p.DATE

    @_('TIME_OPEN error TIME_CLOSE')
    def trkpt_item(self, p):
        print(f"Valor de fecha no válido ('{p.error.value}') en la línea {p.error.lineno}")

    @_('EXTENSIONS_OPEN TPE_OPEN tpe_content TPE_CLOSE EXTENSIONS_CLOSE')
    def trkpt_item(self, p):
        return p.tpe_content

    @_('error TPE_OPEN tpe_content TPE_CLOSE EXTENSIONS_CLOSE')
    def trkpt_item(self, p):
        print('Error: Falta la etiqueta de apertura de </extensions>')
        return p.tpe_content

    @_('EXTENSIONS_OPEN TPE_OPEN tpe_content TPE_CLOSE error')
    def trkpt_item(self, p):
        print('Error: Falta la etiqueta de cierre de <extensions>')
        return p.tpe_content

    @_('EXTENSIONS_OPEN error tpe_content TPE_CLOSE EXTENSIONS_CLOSE')
    def trkpt_item(self, p):
        print('Error: Falta la etiqueta de apertura de </ns3:TrackPointExtension>')
        return p.tpe_content

    @_('EXTENSIONS_OPEN TPE_OPEN tpe_content error EXTENSIONS_CLOSE')
    def trkpt_item(self, p):
        print('Error: Falta la etiqueta de cierre de <ns3:TrackPointExtension>')
        return p.tpe_content

    @_('tpe_content tpe_item')
    def tpe_content(self, p):
        p.tpe_content.append(p.tpe_item)
        return p.tpe_content

    @_('tpe_item')
    def tpe_content(self, p):
        return [p.tpe_item]

    @_('TEMP_OPEN FLOAT TEMP_CLOSE')
    def tpe_item(self, p):
        self.temperature.append(p.FLOAT)
        return p.FLOAT

    @_('error FLOAT TEMP_CLOSE')
    def tpe_item(self, p):
        self.temperature.append(p.FLOAT)
        print('Error: Falta la etiqueta de apertura de </ns3:atemp>')
        return p.FLOAT

    @_('TEMP_OPEN FLOAT error')
    def tpe_item(self, p):
        self.temperature.append(p.FLOAT)
        print('Error: Falta la etiqueta de cierre de <ns3:atemp>')
        return p.FLOAT

    @_('TEMP_OPEN INT TEMP_CLOSE')
    def tpe_item(self, p):
        self.temperature.append(p.INT)
        return p.INT

    @_('error INT TEMP_CLOSE')
    def tpe_item(self, p):
        self.temperature.append(p.INT)
        print('Error: Falta la etiqueta de apertura de </ns3:atemp>')
        return p.INT

    @_('TEMP_OPEN INT error')
    def tpe_item(self, p):
        self.temperature.append(p.INT)
        print('Error: Falta la etiqueta de cierre de <ns3:atemp>')
        return p.INT

    @_('TEMP_OPEN NEGATIVE_NUMBER TEMP_CLOSE')
    def tpe_item(self, p):
        self.temperature.append(p.INT)
        return p.NEGATIVE_NUMBER

    @_('error NEGATIVE_NUMBER TEMP_CLOSE')
    def tpe_item(self, p):
        self.temperature.append(p.INT)
        print('Error: Falta la etiqueta de apertura de </ns3:atemp>')
        return p.NEGATIVE_NUMBER

    @_('TEMP_OPEN NEGATIVE_NUMBER error')
    def tpe_item(self, p):
        self.temperature.append(p.INT)
        print('Error: Falta la etiqueta de cierre de <ns3:atemp>')
        return p.NEGATIVE_NUMBER

    @_('TEMP_OPEN error TEMP_CLOSE')
    def tpe_item(self, p):
        print(f"Valor de temperatura no válido ('{p.error.value}') en la línea {p.error.lineno}")

    @_('HR_OPEN INT HR_CLOSE')
    def tpe_item(self, p):
        self.heart_rate.append(p.INT)
        return p.INT
    
    @_('error INT HR_CLOSE')
    def tpe_item(self, p):
        self.heart_rate.append(p.INT)
        print('Error: Falta la etiqueta de apertura de </ns3:hr>')
        return p.INT

    @_('HR_OPEN INT error')
    def tpe_item(self, p):
        self.heart_rate.append(p.INT)
        print('Error: Falta la etiqueta de cierre de <ns3:hr>')
        return p.INT

    @_('HR_OPEN error HR_CLOSE')
    def tpe_item(self, p):
        print(f"Valor de ritmo cardíaco no válido ('{p.error.value}') en la línea {p.error.lineno}")

    @_('CAD_OPEN INT CAD_CLOSE')
    def tpe_item(self, p):
        self.cadence.append(p.INT)
        return p.INT  
        
    @_('error INT CAD_CLOSE')
    def tpe_item(self, p):
        self.cadence.append(p.INT)
        print('Error: Falta la etiqueta de apertura de </cadence>')
        return p.INT
    
    @_('CAD_OPEN INT error')
    def tpe_item(self, p):
        self.cadence.append(p.INT)
        print('Error: Falta la etiqueta de cierre de <cadence>')
        return p.INT

    @_('CAD_OPEN error CAD_CLOSE')
    def tpe_item(self, p):
        print(f"Valor de cadencia no válido ('{p.error.value}') en la línea {p.error.lineno}")

# json.dumps()
# ensure_ascii = False
# indent = 2
# cls = EnhancedJSONEncoder

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
