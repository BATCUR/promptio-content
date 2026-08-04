"""Tests del renderizador de carruseles.

Cubren las tres cosas que, si se rompen, se publican mal sin que nadie lo
note: el tamaño del lienzo, el desbordamiento del título y la
reproducibilidad de la lámina de cierre.

    cd renderizador && python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import hashlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ_REND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_REND))

import marca  # noqa: E402
from generar_carrusel import planificar, renderizar  # noqa: E402
from guion import Post, buscar_post  # noqa: E402

REPO = RAIZ_REND.parent


def dimensiones_png(ruta: Path) -> tuple[int, int]:
    """Lee ancho y alto del IHDR sin depender de Pillow."""
    datos = ruta.read_bytes()
    if datos[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{ruta} no es un PNG")
    ancho, alto = struct.unpack(">II", datos[16:24])
    return ancho, alto


def sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


class TestDimensiones(unittest.TestCase):
    def test_todas_las_laminas_miden_1080x1350(self):
        laminas = [
            {"tipo": "portada", "texto": "CIERRA LA PUERTA"},
            {"tipo": "cita", "texto": "Hizo exactamente lo que dijiste."},
            {"tipo": "texto", "texto": "Un párrafo de desarrollo cualquiera para la prueba."},
            {"tipo": "cierre", "texto": marca.CIERRE_TEXTO},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            rutas = renderizar(laminas, Path(tmp))
            self.assertEqual(len(rutas), 4)
            for ruta in rutas:
                self.assertEqual(dimensiones_png(ruta), (1080, 1350), f"{ruta.name} no mide 1080x1350")


class TestTituloNoDesborda(unittest.TestCase):
    def _render_titulo(self, titulo: str) -> Path:
        with tempfile.TemporaryDirectory() as tmp:
            rutas = renderizar([{"tipo": "portada", "texto": titulo}], Path(tmp))
            destino = Path(tempfile.mkdtemp()) / rutas[0].name
            destino.write_bytes(rutas[0].read_bytes())
            return destino

    def test_titulo_corto(self):
        ruta = self._render_titulo("ROL")
        self.assertEqual(dimensiones_png(ruta), (1080, 1350))

    def test_titulo_largo_no_desborda(self):
        # Un título de portada realista pero mucho más largo que el habitual.
        largo = "POR QUÉ SÉ MÁS ESPECÍFICO NO ES UN CONSEJO ÚTIL PARA NADIE"
        ruta = self._render_titulo(largo)
        self.assertEqual(dimensiones_png(ruta), (1080, 1350))

    def test_palabra_sin_espacios_no_desborda(self):
        # Peor caso de layout: no hay dónde partir la línea.
        ruta = self._render_titulo("CONTEXTUALIZACIONES" * 2)
        self.assertEqual(dimensiones_png(ruta), (1080, 1350))

    def test_texto_imposible_falla_en_vez_de_recortar(self):
        # Si no cabe ni al tamaño mínimo, el renderizador debe abortar:
        # publicar una lámina con el texto cortado es peor que no publicar.
        imposible = "PALABRA " * 400
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                renderizar([{"tipo": "portada", "texto": imposible}], Path(tmp))


class TestLaminaDeCierre(unittest.TestCase):
    def _render_cierre(self) -> Path:
        tmp = Path(tempfile.mkdtemp())
        rutas = renderizar([{"tipo": "cierre", "texto": marca.CIERRE_TEXTO}], tmp)
        return rutas[0]

    def test_es_identica_entre_ejecuciones(self):
        # Dos renders independientes, con su propio arranque de Chromium.
        primera = self._render_cierre()
        segunda = self._render_cierre()
        self.assertEqual(
            sha(primera), sha(segunda),
            "La lámina de cierre cambió entre ejecuciones: se rompe la consistencia de marca.",
        )

    def test_no_depende_del_largo_del_carrusel(self):
        # Regresión: al capturar las láminas apiladas, la posición de scroll
        # cambiaba el rasterizado y el cierre de un carrusel de 3 no coincidía
        # con el de uno de 5. Un carrusel corto y uno largo deben cerrar igual.
        def cierre_de(n: int) -> str:
            laminas = [{"tipo": "portada", "texto": "TÍTULO"}]
            laminas += [{"tipo": "texto", "texto": f"Lámina {i}."} for i in range(n)]
            laminas.append({"tipo": "cierre", "texto": marca.CIERRE_TEXTO})
            return sha(renderizar(laminas, Path(tempfile.mkdtemp()))[-1])

        self.assertEqual(cierre_de(1), cierre_de(4),
                         "El cierre cambia según el largo del carrusel.")

    def test_no_depende_del_resto_del_carrusel(self):
        # La misma lámina, renderizada sola y al final de un carrusel largo,
        # tiene que salir idéntica.
        sola = self._render_cierre()
        laminas = [
            {"tipo": "portada", "texto": "UN TÍTULO CUALQUIERA"},
            {"tipo": "texto", "texto": "Texto de relleno."},
            {"tipo": "cierre", "texto": marca.CIERRE_TEXTO},
        ]
        tmp = Path(tempfile.mkdtemp())
        rutas = renderizar(laminas, tmp)
        self.assertEqual(sha(sola), sha(rutas[-1]))


class TestPlanificacion(unittest.TestCase):
    def _post(self, **kw) -> Post:
        base = dict(id="s9p9", titulo_calendario="Prueba", formato="carrusel",
                    fecha="2026-08-03", hora="18:30", semana=9,
                    titulo="TÍTULO", cita="Una cita.", desarrollo="Un párrafo.")
        base.update(kw)
        return Post(**base)

    def test_siempre_termina_en_cierre(self):
        for modo_post in (self._post(), self._post(desarrollo="Uno.\n\nDos.\n\nTres.")):
            laminas = planificar(modo_post)
            self.assertEqual(laminas[-1]["tipo"], "cierre")
            self.assertEqual(laminas[0]["tipo"], "portada")

    def test_solo_hay_una_lamina_de_cierre(self):
        laminas = planificar(self._post(desarrollo="Uno.\n\nDos."))
        self.assertEqual(sum(1 for l in laminas if l["tipo"] == "cierre"), 1)

    def test_falta_un_campo_y_no_planifica(self):
        with self.assertRaises(ValueError):
            planificar(self._post(cita=""))
        with self.assertRaises(ValueError):
            planificar(self._post(titulo=""))

    def test_desarrollo_largo_se_trocea(self):
        largo = " ".join(f"Frase número {i} de relleno para la prueba." for i in range(30))
        laminas = planificar(self._post(desarrollo=largo))
        textos = [l for l in laminas if l["tipo"] == "texto"]
        self.assertGreater(len(textos), 1, "Un desarrollo largo debería ocupar varias láminas")
        for l in textos:
            self.assertLessEqual(len(l["texto"]), 400)


class TestGuionReal(unittest.TestCase):
    def test_post_1_se_lee_del_repo(self):
        post = buscar_post("s1p1", REPO)
        self.assertEqual(post.titulo, "CIERRA LA PUERTA")
        self.assertTrue(post.cita)
        self.assertTrue(post.desarrollo)
        self.assertGreaterEqual(len(post.slides), 4, "El Post 1 detalla sus láminas en **Slides:**")

    def test_la_lamina_heredada_no_se_renderiza(self):
        # El guion del Post 1 marca su última lámina como fija del template;
        # el renderizador la pone por su cuenta y no debe duplicarla.
        post = buscar_post("s1p1", REPO)
        for texto in post.slides:
            self.assertNotIn("Lámina fija", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
