#!/usr/bin/env python3
"""Microservicio HTTP mínimo para que n8n pida carruseles.

Sustituye a los endpoints de Canva: n8n hace un POST con el id del post y
recibe la lista de láminas, luego se descarga cada PNG. Mismo patrón que
tenía con la API de Canva (crear trabajo -> obtener URLs -> descargar),
así que el resto del pipeline no cambia.

    POST /render      {"id": "s1p1", "modo": "campos"}
    GET  /laminas/<semana>/<post>/<archivo>.png
    GET  /salud

Autenticación: cabecera `X-Token` contra la variable de entorno
PROMPTIO_TOKEN. Si no está definida, el servicio se niega a arrancar: no
tiene sentido exponer un endpoint que escribe en disco sin ninguna
protección.

    PROMPTIO_TOKEN=... python3 servicio.py --puerto 8099

Se usa http.server a propósito: el único cliente es n8n en la misma
máquina, y así el renderizador no arrastra más dependencias que Playwright.
No lo publiques en internet — ponlo a escuchar en localhost y que n8n lo
llame por ahí.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generar_carrusel import RAIZ, generar  # noqa: E402

TOKEN = os.environ.get("PROMPTIO_TOKEN", "")
BASE_PUBLICA = os.environ.get("PROMPTIO_BASE_URL", "")
IMAGENES = RAIZ / "imagenes"

# Un render a la vez: Chromium con varias instancias en paralelo en un VPS
# pequeño es la forma más fácil de quedarse sin memoria.
_cerrojo = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = "promptio-renderizador"

    def log_message(self, formato, *args):  # menos ruido en journalctl
        sys.stderr.write("%s - %s\n" % (self.address_string(), formato % args))

    def _json(self, codigo: int, cuerpo: dict):
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def _autorizado(self) -> bool:
        return hmac.compare_digest(self.headers.get("X-Token", ""), TOKEN)

    def do_GET(self):
        ruta = urlparse(self.path).path
        if ruta == "/salud":
            return self._json(200, {"estado": "ok"})
        if not self._autorizado():
            return self._json(401, {"error": "token invalido"})
        if ruta.startswith("/laminas/"):
            return self._servir_png(ruta[len("/laminas/"):])
        self._json(404, {"error": "ruta desconocida"})

    def _servir_png(self, relativa: str):
        destino = (IMAGENES / unquote(relativa)).resolve()
        # No dejar salir del árbol de imágenes con ../
        if not str(destino).startswith(str(IMAGENES.resolve())) or not destino.is_file():
            return self._json(404, {"error": "lamina no encontrada"})
        datos = destino.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_POST(self):
        if not self._autorizado():
            return self._json(401, {"error": "token invalido"})
        if urlparse(self.path).path != "/render":
            return self._json(404, {"error": "ruta desconocida"})

        try:
            largo = int(self.headers.get("Content-Length", 0))
            peticion = json.loads(self.rfile.read(largo) or b"{}")
        except (ValueError, json.JSONDecodeError) as e:
            return self._json(400, {"error": f"cuerpo no es JSON valido: {e}"})

        id_post = peticion.get("id")
        if not id_post:
            return self._json(400, {"error": "falta el campo 'id'"})
        modo = peticion.get("modo", "campos")

        with _cerrojo:
            try:
                res = generar(id_post, modo=modo)
            except Exception as e:
                # El pipeline de n8n corta aquí y avisa por Telegram.
                return self._json(422, {"error": str(e), "id": id_post, "modo": modo})

        semana = res["directorio"].rsplit("/", 2)[-2]
        for lamina in res["laminas"]:
            lamina["url"] = f"{BASE_PUBLICA}/laminas/{semana}/{res['id']}/{lamina['archivo']}"
        return self._json(200, res)


def main() -> int:
    ap = argparse.ArgumentParser(description="Microservicio de render de carruseles PROMPTIO.")
    ap.add_argument("--puerto", type=int, default=8099)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    if not TOKEN:
        print("ERROR: define PROMPTIO_TOKEN antes de arrancar el servicio.", file=sys.stderr)
        return 1

    global BASE_PUBLICA
    if not BASE_PUBLICA:
        BASE_PUBLICA = f"http://{args.host}:{args.puerto}"

    servidor = ThreadingHTTPServer((args.host, args.puerto), Handler)
    print(f"Renderizador escuchando en http://{args.host}:{args.puerto}", file=sys.stderr)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
