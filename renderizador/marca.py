"""Constantes de marca de PROMPTIO.

Todo lo que no debe variar entre posts vive aquí. Si un valor de este
archivo cambia, cambia la identidad visual de toda la cuenta: trátalo
como un cambio de marca, no como un ajuste de código.
"""

# Lienzo (formato vertical de Instagram)
ANCHO = 1080
ALTO = 1350

# Paleta, heredada de la landing (index.html de promptio-landing)
CREMA = "#F4EEDD"
NAVY = "#1C2B45"
DORADO = "#D9A441"
TEAL = "#3E8C86"

# Retícula
MARGEN = 96          # padding lateral de todas las láminas
CAJA_TOP = 220       # inicio del área de texto
CAJA_BOTTOM = 1000   # fin del área de texto (deja aire para la línea dorada)

# Línea de acento dorada: posición FIJA, idéntica en todas las portadas.
# No depende del largo del título ni del post.
LINEA_X = MARGEN
LINEA_Y = 1030
LINEA_ANCHO = 180
LINEA_ALTO = 12

# Gato: posición FIJA en todas las láminas excepto la de cierre.
GATO_TAM = 150
GATO_RIGHT = 72
GATO_BOTTOM = 72

# Tipografía
TITULO_MAX = 190     # px, punto de partida del autoajuste
TITULO_MIN = 64      # px, por debajo de esto se considera que no cabe
CUERPO_MAX = 76
CUERPO_MIN = 34

# Lámina de cierre: fija, idéntica en todos los carruseles, sin excepción.
CIERRE_TEXTO = "LA CLARIDAD EN TU INSTRUCCIÓN DETERMINA LA CALIDAD DEL RESULTADO."
CIERRE_TAM = 76      # tamaño fijo, no autoajustado: garantiza reproducibilidad
