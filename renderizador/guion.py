"""Lectura de calendario.md y guiones/semana-N.md.

Replica el mismo parseo que hacen los nodos Code del workflow de n8n. Si
cambias un regex aquí, cámbialo también en workflow-publicacion.json.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

LINEA_POST = re.compile(
    r"^- \*\*(?P<titulo>.+?)\*\* · \*(?P<formato>.+?)\* · "
    r"`(?P<id>[a-z0-9]+)` · `(?P<fecha>\d{4}-\d{2}-\d{2}) (?P<hora>\d{2}:\d{2})`"
)

# El texto de una lámina dentro del campo **Slides:**
CABECERA_SLIDE = re.compile(r"^\*Slide\s+(\d+)\s*[—-]\s*(.+?)\*\s*$")

# Una lámina que solo dice "esto ya está en la plantilla" no se renderiza:
# la de cierre la añade el renderizador por su cuenta.
LAMINA_HEREDADA = re.compile(r"lámina fija|brand template|no se toca", re.I)


@dataclass
class Post:
    id: str
    titulo_calendario: str
    formato: str
    fecha: str
    hora: str
    semana: int
    titulo: str = ""
    cita: str = ""
    desarrollo: str = ""
    caption: str = ""
    comentario: str = ""
    slides: list[str] = field(default_factory=list)

    @property
    def completo(self) -> bool:
        return bool(self.titulo and self.cita and self.desarrollo)


def _campo(bloque: str, *nombres: str) -> str:
    """Extrae **Nombre:** del bloque de un guion.

    Se aceptan varios nombres para el mismo campo (compatibilidad con los
    guiones que todavía dicen "(autofill)", de cuando esto lo hacía Canva).

    El `[ \\t]*` tras la cabecera es deliberado: con `\\s*`, el motor de
    regex se come los saltos de línea de forma codiciosa y no los devuelve,
    así que un campo vacío captura la cabecera del campo siguiente.
    """
    for nombre in nombres:
        patron = re.compile(
            r"\*\*" + re.escape(nombre) + r":\*\*[ \t]*(.*?)"
            r"(?=\n\s*\*\*[^*]+:\*\*|\n---|\Z)",
            re.S,
        )
        m = patron.search(bloque)
        if not m:
            continue
        valor = m.group(1).strip()
        if re.fullmatch(r"\*\*[^*]+:\*\*", valor):
            continue
        if valor:
            return valor
    return ""


def _laminas_de_slides(bloque: str) -> list[str]:
    """Saca el texto de cada lámina del campo **Slides:**, si lo hay.

    Formato esperado:

        *Slide 2 — La escena*
        > Le pides a alguien que cierre la puerta.
        >
        > La cierra.
    """
    crudo = _campo(bloque, "Slides")
    if not crudo:
        return []

    laminas: list[str] = []
    actual: list[str] | None = None
    for linea in crudo.split("\n"):
        if CABECERA_SLIDE.match(linea.strip()):
            if actual is not None:
                laminas.append("\n".join(actual).strip())
            actual = []
            continue
        if actual is None:
            continue
        if linea.startswith(">"):
            actual.append(linea.lstrip(">").strip())
        elif not linea.strip():
            actual.append("")
    if actual is not None:
        laminas.append("\n".join(actual).strip())

    limpias = []
    for l in laminas:
        texto = re.sub(r"^#+\s*", "", l, flags=re.M).strip()
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        if texto and not LAMINA_HEREDADA.search(texto):
            limpias.append(texto)
    return limpias


def leer_calendario(ruta: Path) -> list[Post]:
    posts = []
    for linea in ruta.read_text(encoding="utf-8").split("\n"):
        m = LINEA_POST.match(linea)
        if not m:
            continue
        d = m.groupdict()
        posts.append(
            Post(
                id=d["id"],
                titulo_calendario=d["titulo"],
                formato=d["formato"],
                fecha=d["fecha"],
                hora=d["hora"],
                semana=int(re.match(r"^s(\d+)", d["id"]).group(1)),
            )
        )
    if not posts:
        raise ValueError(f"No se pudo parsear ningún post de {ruta}. ¿Cambió el formato de las líneas?")
    return posts


def cargar_guion(post: Post, dir_guiones: Path) -> Post:
    ruta = dir_guiones / f"semana-{post.semana}.md"
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}")

    bloques = re.split(r"^## ", ruta.read_text(encoding="utf-8"), flags=re.M)[1:]
    bloque = next((b for b in bloques if post.id in b), None)
    if bloque is None:
        raise ValueError(f"No hay bloque de guion con el id {post.id} en {ruta}")

    post.titulo = _campo(bloque, "Título (autofill)", "Título", "Titulo")
    post.cita = _campo(bloque, "Cita (autofill)", "Cita")
    post.desarrollo = _campo(bloque, "Desarrollo (autofill)", "Desarrollo")
    post.caption = _campo(bloque, "Caption")
    post.comentario = _campo(bloque, "Comentario funcional")
    post.slides = _laminas_de_slides(bloque)
    return post


def buscar_post(id_post: str, raiz: Path) -> Post:
    posts = leer_calendario(raiz / "calendario.md")
    post = next((p for p in posts if p.id == id_post), None)
    if post is None:
        disponibles = ", ".join(p.id for p in posts)
        raise ValueError(f"No existe el post '{id_post}'. Hay: {disponibles}")
    return cargar_guion(post, raiz / "guiones")
