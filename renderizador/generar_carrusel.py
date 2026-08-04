#!/usr/bin/env python3
"""Renderiza el carrusel de un post de PROMPTIO como PNG de 1080x1350.

Sustituye a la API de autofill de Canva: mismo resultado visual, sin
servicios externos ni plan Enterprise.

Uso:
    python3 generar_carrusel.py s1p1
    python3 generar_carrusel.py s1p1 --modo slides
    python3 generar_carrusel.py s1p1 --salida /tmp/prueba --abrir-html
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import marca  # noqa: E402
from guion import Post, buscar_post  # noqa: E402
from plantilla import construir_html  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
MAX_CARACTERES_LAMINA = 240


def _trocear(texto: str) -> list[str]:
    """Parte el desarrollo en láminas: primero por párrafos y, si un
    párrafo sigue siendo largo, por frases. Determinista."""
    trozos: list[str] = []
    for parrafo in [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]:
        if len(parrafo) <= MAX_CARACTERES_LAMINA:
            trozos.append(parrafo)
            continue
        frases = re.split(r"(?<=[.!?])\s+", parrafo)
        actual = ""
        for frase in frases:
            if actual and len(actual) + 1 + len(frase) > MAX_CARACTERES_LAMINA:
                trozos.append(actual.strip())
                actual = frase
            else:
                actual = f"{actual} {frase}".strip()
        if actual:
            trozos.append(actual.strip())
    return trozos


def planificar(post: Post, modo: str = "campos") -> list[dict]:
    """Decide qué láminas se van a renderizar.

    modo "campos" (por defecto): portada + cita + desarrollo troceado.
    modo "slides": usa el campo **Slides:** del guion, que lleva el texto
    lámina a lámina cuando el guion lo detalla.

    En ambos casos la lámina de cierre se añade siempre al final, y no se
    puede desactivar: es una regla de marca, no una opción.
    """
    if not post.titulo:
        raise ValueError(f"El post {post.id} no tiene **Título** en su guion.")

    laminas: list[dict] = [{"tipo": "portada", "texto": post.titulo}]

    if modo == "slides":
        if len(post.slides) < 2:
            raise ValueError(
                f"El post {post.id} no tiene suficientes láminas en **Slides:** "
                f"({len(post.slides)}). Usa --modo campos."
            )
        for texto in post.slides[1:]:
            laminas.append({"tipo": "texto", "texto": texto})
    else:
        if not post.cita:
            raise ValueError(f"El post {post.id} no tiene **Cita** en su guion.")
        if not post.desarrollo:
            raise ValueError(f"El post {post.id} no tiene **Desarrollo** en su guion.")
        laminas.append({"tipo": "cita", "texto": post.cita})
        for trozo in _trocear(post.desarrollo):
            laminas.append({"tipo": "texto", "texto": trozo})

    laminas.append({"tipo": "cierre", "texto": marca.CIERRE_TEXTO})
    return laminas


def ejecutable_chromium() -> str | None:
    """Chromium a usar.

    Playwright espera una build concreta bajo su carpeta de navegadores y
    falla si la versión instalada no coincide exactamente. En un VPS donde
    Chromium ya viene con el sistema (o con otra build), esto evita tener
    que descargar otra copia: se apunta al binario existente.

    Orden: $PROMPTIO_CHROMIUM > build más nueva bajo
    $PLAYWRIGHT_BROWSERS_PATH > chromium del sistema > el de Playwright.
    """
    explicito = os.environ.get("PROMPTIO_CHROMIUM")
    if explicito:
        return explicito

    base = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    if base.is_dir():
        candidatos = sorted(base.glob("chromium-*/chrome-linux/chrome"))
        if candidatos:
            return str(candidatos[-1])

    for ruta in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if Path(ruta).exists():
            return ruta
    return None


def renderizar(laminas: list[dict], destino: Path, prefijo: str = "lamina",
               guardar_html: bool = False) -> list[Path]:
    """Abre Chromium headless y captura cada lámina como PNG."""
    from playwright.sync_api import sync_playwright

    destino.mkdir(parents=True, exist_ok=True)
    html = construir_html(laminas)

    # El HTML se carga desde disco, no con set_content: un documento
    # about:blank no puede cargar subrecursos file://, y las @font-face se
    # quedarían fuera sin dar error. Se vería una sans genérica en vez de
    # Anton, que es justo el tipo de fallo que nadie nota hasta que está
    # publicado.
    ruta_html = destino / "debug.html"
    ruta_html.write_text(html, encoding="utf-8")

    rutas: list[Path] = []
    with sync_playwright() as p:
        opciones = {"args": ["--force-color-profile=srgb", "--font-render-hinting=none"]}
        binario = ejecutable_chromium()
        if binario:
            opciones["executable_path"] = binario
        navegador = p.chromium.launch(**opciones)
        pagina = navegador.new_page(
            viewport={"width": marca.ANCHO, "height": marca.ALTO},
            device_scale_factor=1,
        )
        pagina.goto(ruta_html.resolve().as_uri(), wait_until="load")
        pagina.evaluate("document.fonts.ready")

        # Hay que forzar la carga antes de comprobar: una familia que la
        # lámina no usa figura como "unloaded" aunque esté disponible.
        fuentes_ok = pagina.evaluate("""async () => {
            await Promise.all([
              document.fonts.load('400 100px Anton'),
              document.fonts.load('600 100px Inter'),
              document.fonts.load('700 100px Inter'),
            ]);
            return document.fonts.check('400 100px Anton')
                && document.fonts.check('600 100px Inter')
                && document.fonts.check('700 100px Inter');
        }""")
        if not fuentes_ok:
            navegador.close()
            raise RuntimeError(
                "Anton o Inter no se cargaron: Chromium renderizaría con una fuente "
                "de sustitución y el resultado no sería de marca. Revisa "
                "renderizador/assets/fonts/."
            )

        ajustes = pagina.evaluate("window.__ajustar()")

        desbordes = [a for a in ajustes if a["desborda"]]
        if desbordes:
            ids = ", ".join(d["id"] for d in desbordes)
            navegador.close()
            raise RuntimeError(
                f"El texto no cabe ni al tamaño mínimo en: {ids}. "
                f"Acorta el texto del guion o revisa marca.py."
            )

        recorte = {"x": 0, "y": 0, "width": marca.ANCHO, "height": marca.ALTO}
        for i in range(1, len(laminas) + 1):
            ruta = destino / f"{prefijo}-{i:02d}.png"
            pagina.evaluate("id => window.__aislar(id)", f"lamina-{i}")
            pagina.screenshot(path=str(ruta), clip=recorte)
            rutas.append(ruta)
        navegador.close()

    if not guardar_html:
        ruta_html.unlink(missing_ok=True)
    return rutas


def generar(id_post: str, modo: str = "campos", salida: Path | None = None,
            raiz: Path = RAIZ, guardar_html: bool = False) -> dict:
    post = buscar_post(id_post, raiz)
    laminas = planificar(post, modo)
    destino = salida or (raiz / "imagenes" / f"semana-{post.semana}" / post.id)
    rutas = renderizar(laminas, destino, prefijo=post.id, guardar_html=guardar_html)
    return {
        "id": post.id,
        "titulo": post.titulo,
        "formato": post.formato,
        "modo": modo,
        "total": len(rutas),
        "directorio": str(destino),
        "laminas": [
            {"pagina": i, "tipo": l["tipo"], "archivo": r.name, "ruta": str(r)}
            for i, (l, r) in enumerate(zip(laminas, rutas), start=1)
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Renderiza el carrusel de un post de PROMPTIO.")
    ap.add_argument("id_post", help="Id del post, tal como aparece en calendario.md (ej. s1p1)")
    ap.add_argument("--modo", choices=["campos", "slides"], default="campos",
                    help="campos: portada + cita + desarrollo. slides: usa el campo **Slides:** del guion.")
    ap.add_argument("--salida", type=Path, default=None, help="Directorio de salida")
    ap.add_argument("--raiz", type=Path, default=RAIZ, help="Raíz del repo promptio-content")
    ap.add_argument("--abrir-html", action="store_true", help="Guarda también debug.html junto a los PNG")
    ap.add_argument("--json", action="store_true", help="Salida en JSON (lo usa el microservicio)")
    args = ap.parse_args()

    try:
        res = generar(args.id_post, args.modo, args.salida, args.raiz, args.abrir_html)
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"{res['id']} — {res['titulo']}")
        print(f"modo {res['modo']}, {res['total']} láminas en {res['directorio']}")
        for l in res["laminas"]:
            print(f"  {l['pagina']:>2}. {l['tipo']:<8} {l['archivo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
