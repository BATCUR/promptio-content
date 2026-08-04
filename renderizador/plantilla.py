"""Construcción del HTML que Chromium convierte en PNG.

El layout vive aquí en CSS, no en la lógica de Python: así el resultado se
puede abrir en un navegador y depurar a ojo.
"""
from __future__ import annotations

import base64
import html
from functools import lru_cache
from pathlib import Path

import marca

ASSETS = Path(__file__).resolve().parent / "assets"


def _svg(nombre: str) -> str:
    return (ASSETS / nombre).read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _fuente(archivo: str) -> str:
    """Devuelve la fuente como data URI.

    No vale con enlazar el .ttf por file://: las @font-face están sujetas a
    CORS y un documento file:// tiene origen opaco, así que Chromium las
    descarta en silencio y cae en una sans de sustitución. Incrustarlas
    también hace que el HTML sea autocontenido y se pueda abrir en
    cualquier máquina para depurar.
    """
    datos = (ASSETS / "fonts" / archivo).read_bytes()
    return "data:font/ttf;base64," + base64.b64encode(datos).decode("ascii")


def _css() -> str:
    return f"""
@font-face {{
  font-family: 'Anton';
  src: url('{_fuente("Anton-Regular.ttf")}') format('truetype');
  font-weight: 400; font-style: normal; font-display: block;
}}
@font-face {{
  font-family: 'Inter';
  src: url('{_fuente("Inter-400.ttf")}') format('truetype');
  font-weight: 400; font-style: normal; font-display: block;
}}
@font-face {{
  font-family: 'Inter';
  src: url('{_fuente("Inter-600.ttf")}') format('truetype');
  font-weight: 600; font-style: normal; font-display: block;
}}
@font-face {{
  font-family: 'Inter';
  src: url('{_fuente("Inter-700.ttf")}') format('truetype');
  font-weight: 700; font-style: normal; font-display: block;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #888; }}

.lamina {{
  position: relative;
  width: {marca.ANCHO}px;
  height: {marca.ALTO}px;
  contain: paint;
  background: {marca.CREMA};
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* Modo de captura: cada lámina se lleva al origen del viewport y se
   fotografía ahí. Si se capturan apiladas, la posición de scroll cambia el
   rasterizado subpíxel del texto y la lámina de cierre sale distinta según
   cuántas láminas la precedan — que es justo lo que la marca no permite. */
body.modo-aislado .lamina {{ position: fixed; top: 0; left: 0; }}
body.modo-aislado .lamina:not(.activa) {{ visibility: hidden; }}

.caja {{
  position: absolute;
  left: {marca.MARGEN}px;
  right: {marca.MARGEN}px;
  top: {marca.CAJA_TOP}px;
  height: {marca.CAJA_BOTTOM - marca.CAJA_TOP}px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}}

.titulo {{
  font-family: 'Anton', sans-serif;
  font-weight: 400;
  text-transform: uppercase;
  color: {marca.NAVY};
  line-height: 0.92;
  letter-spacing: -0.5px;
  overflow-wrap: anywhere;
}}

.cuerpo {{
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: {marca.NAVY};
  line-height: 1.28;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}}
.cuerpo.cita {{ color: {marca.TEAL}; font-weight: 700; }}

/* Posición fija: no depende del largo del título ni del post. */
.linea-acento {{
  position: absolute;
  left: {marca.LINEA_X}px;
  top: {marca.LINEA_Y}px;
  width: {marca.LINEA_ANCHO}px;
  height: {marca.LINEA_ALTO}px;
  border-radius: {marca.LINEA_ALTO // 2}px;
  background: {marca.DORADO};
}}

/* Posición fija en todas las láminas menos la de cierre. */
.gato {{
  position: absolute;
  right: {marca.GATO_RIGHT}px;
  bottom: {marca.GATO_BOTTOM}px;
  width: {marca.GATO_TAM}px;
  height: {marca.GATO_TAM}px;
}}
.gato svg {{ width: 100%; height: 100%; display: block; }}

/* Lámina de cierre: layout fijo, sin autoajuste, para que sea reproducible. */
.cierre {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 96px;
  padding: 0 {marca.MARGEN}px;
}}
.cierre-texto {{
  font-family: 'Anton', sans-serif;
  text-transform: uppercase;
  color: {marca.NAVY};
  font-size: {marca.CIERRE_TAM}px;
  line-height: 1.06;
  text-align: center;
  letter-spacing: -0.5px;
}}
.cierre-logo {{ width: 300px; height: 300px; }}
.cierre-logo svg {{ width: 100%; height: 100%; display: block; }}
"""


_AJUSTE_JS = """
// Autoajuste por búsqueda binaria sobre enteros: mismo input -> mismo
// tamaño, siempre. Marca data-desborda si ni al mínimo cabe el texto.
window.__ajustar = function () {
  document.querySelectorAll('[data-fit]').forEach(function (el) {
    var min = parseInt(el.dataset.min, 10);
    var max = parseInt(el.dataset.max, 10);
    var caja = el.parentElement;
    var lo = min, hi = max, mejor = min;
    while (lo <= hi) {
      var mid = Math.floor((lo + hi) / 2);
      el.style.fontSize = mid + 'px';
      var cabe = el.scrollHeight <= caja.clientHeight && el.scrollWidth <= caja.clientWidth;
      if (cabe) { mejor = mid; lo = mid + 1; } else { hi = mid - 1; }
    }
    el.style.fontSize = mejor + 'px';
    el.dataset.ajustado = String(mejor);
    var desborda = el.scrollHeight > caja.clientHeight || el.scrollWidth > caja.clientWidth;
    el.dataset.desborda = desborda ? '1' : '0';
  });
  return Array.from(document.querySelectorAll('[data-fit]')).map(function (el) {
    return { id: el.closest('.lamina').id, tam: Number(el.dataset.ajustado), desborda: el.dataset.desborda === '1' };
  });
};

// Deja una sola lámina visible, anclada al origen del viewport.
window.__aislar = function (id) {
  document.body.classList.add('modo-aislado');
  document.querySelectorAll('.lamina').forEach(function (el) {
    el.classList.toggle('activa', el.id === id);
  });
  window.scrollTo(0, 0);
};
"""


def _lamina_portada(idx: int, titulo: str) -> str:
    return f"""
<div class="lamina" id="lamina-{idx}">
  <div class="caja">
    <div class="titulo" data-fit="titulo" data-min="{marca.TITULO_MIN}" data-max="{marca.TITULO_MAX}">{html.escape(titulo)}</div>
  </div>
  <div class="linea-acento"></div>
  <div class="gato">{_svg("gato.svg")}</div>
</div>"""


def _lamina_texto(idx: int, texto: str, cita: bool = False) -> str:
    clase = "cuerpo cita" if cita else "cuerpo"
    return f"""
<div class="lamina" id="lamina-{idx}">
  <div class="caja">
    <div class="{clase}" data-fit="cuerpo" data-min="{marca.CUERPO_MIN}" data-max="{marca.CUERPO_MAX}">{html.escape(texto)}</div>
  </div>
  <div class="gato">{_svg("gato.svg")}</div>
</div>"""


def _lamina_cierre(idx: int) -> str:
    # Sin gato y sin autoajuste: idéntica en todos los carruseles.
    return f"""
<div class="lamina cierre" id="lamina-{idx}">
  <div class="cierre-texto">{html.escape(marca.CIERRE_TEXTO)}</div>
  <div class="cierre-logo">{_svg("logo-promptio.svg")}</div>
</div>"""


def construir_html(laminas: list[dict]) -> str:
    cuerpos = []
    for i, l in enumerate(laminas, start=1):
        if l["tipo"] == "portada":
            cuerpos.append(_lamina_portada(i, l["texto"]))
        elif l["tipo"] == "cierre":
            cuerpos.append(_lamina_cierre(i))
        else:
            cuerpos.append(_lamina_texto(i, l["texto"], cita=l["tipo"] == "cita"))
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><style>{_css()}</style></head>
<body>{"".join(cuerpos)}<script>{_AJUSTE_JS}</script></body></html>"""
