# Automatización de publicación — n8n + renderizador local + Postiz + Meta

Cómo importar, configurar y probar `workflow-publicacion.json` en la
instancia de n8n del VPS de Hetzner, y cómo usar el renderizador de
carruseles por separado.

> **Léelo antes de importar.** El JSON del workflow se escribió a mano
> contra la documentación de cada API, no se exportó de un workflow que ya
> hubiera corrido. El renderizador sí está probado y funcionando (14 tests
> en verde), pero el workflow que lo llama no se ha ejecutado nunca dentro
> de n8n. Da por hecho que tendrás que tocar algún nodo tras importar.

Canva queda fuera: la API de autofill exige plan Enterprise. En su lugar,
las láminas se generan en el propio VPS con Chromium headless.

---

## Qué hace

```
Trigger 09:00 → Configuración
      ↓
GitHub: calendario.md + log.md
      ↓
Seleccionar post de hoy          ← fecha == hoy Y no está en log.md
      ↓
GitHub: guiones/semana-N.md → Extraer datos → Verificar
      ↓ completo                              ↓ falta algo
Renderizador: POST /render                 Telegram → Fin
      ↓
Evaluar render ──── error ──→ Telegram → Fin
      ↓ listo
Descargar láminas → Postiz: subir → Postiz: publicar
      ↓
Esperar 3 min → Meta: medios recientes → emparejar por caption
      ↓                          ↓ no encontrado
Meta: comentario           Telegram: publicado sin comentario
      ↓                          ↓
      └────────→ log.md ←────────┘
                    ↓
            Telegram: confirmación
```

Comparado con la versión de Canva, desaparecen diez nodos (dos bucles de
polling, dos jobs asíncronos y sus evaluadores) y quedan tres: llamar al
renderizador, evaluar la respuesta y descargar. El resto del pipeline
—Postiz, comentario funcional, `log.md`, anti-duplicado— no cambia.

`Evaluar render` no se limita a mirar si hubo error: comprueba que vengan
al menos dos láminas y que **la última sea la de cierre**. Un carrusel sin
su lámina de cierre no se publica.

---

## El renderizador

```
renderizador/
├── generar_carrusel.py   CLI: renderiza el carrusel de un post
├── servicio.py           microservicio HTTP que llama n8n
├── guion.py              lee calendario.md y guiones/semana-N.md
├── plantilla.py          HTML/CSS de las láminas
├── marca.py              colores, retícula y textos fijos de marca
├── requirements.txt
├── assets/
│   ├── gato.svg
│   ├── logo-promptio.svg
│   └── fonts/            Anton e Inter, vendorizadas
└── tests/test_render.py
```

Salida en `imagenes/semana-N/<id>/<id>-01.png`, `-02.png`…

### Uso standalone, sin n8n

```bash
cd renderizador
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium      # solo la primera vez

python3 generar_carrusel.py s1p1                    # modo campos
python3 generar_carrusel.py s1p1 --modo slides      # una lámina por Slide del guion
python3 generar_carrusel.py s1p1 --salida /tmp/prueba --abrir-html
```

`--abrir-html` deja un `debug.html` junto a los PNG: ábrelo en un navegador
para ajustar el layout sin volver a renderizar.

**Los dos modos:**

- **`campos`** (por defecto) — portada con el **Título**, una lámina con la
  **Cita**, una o varias con el **Desarrollo** troceado por párrafos, y el
  cierre. Es el que replica lo que hacía el Brand Template de Canva con sus
  tres campos.
- **`slides`** — usa el campo **Slides:** del guion, que lleva el texto
  lámina a lámina cuando el guion lo detalla. Para el Post 1 da 6 láminas
  en vez de 4, y se parece más al carrusel diseñado.

Cambia el modo por defecto en el campo `renderizadorModo` del nodo
`Configuracion`.

### Tests

```bash
cd renderizador && python3 -m unittest discover -s tests -v
```

Cubren lo que rompería la marca sin avisar:

- **Dimensiones**: cada lámina mide exactamente 1080 × 1350.
- **Desbordamiento del título**: títulos cortos, largos y una palabra sin
  espacios que no cabe en una línea. Si un texto no cabe ni al tamaño
  mínimo, el renderizador **aborta** en vez de recortar: publicar una
  lámina con el texto cortado es peor que no publicar.
- **Reproducibilidad del cierre**: la lámina de cierre tiene que salir
  byte a byte idéntica entre ejecuciones, sola o al final de un carrusel, y
  con independencia de cuántas láminas la precedan.

Ese último test detectó un fallo real durante el desarrollo: capturando las
láminas apiladas en una sola página, la posición de scroll cambiaba el
rasterizado subpíxel del texto, y el cierre de un carrusel de 4 láminas no
coincidía con el de uno de 6. Ahora cada lámina se captura anclada al
origen del viewport. Si tocas `plantilla.py`, ese test es el que avisa de
que lo has vuelto a romper.

### Qué está fijo y no debe tocarse por post

En `marca.py`:

- Lienzo 1080 × 1350 y paleta (`#F4EEDD`, `#1C2B45`, `#D9A441`, `#3E8C86`).
- Posición de la línea dorada: siempre en las mismas coordenadas, no
  depende del largo del título.
- Posición del gato: esquina inferior derecha, idéntica en todas las
  láminas salvo la de cierre, donde no aparece.
- Texto de la lámina de cierre.

`planificar()` añade la lámina de cierre siempre y no admite desactivarla.

---

## Prerequisitos

### 1. VPS: Chromium

El renderizador corre en el mismo VPS que n8n. Necesita Chromium y sus
librerías de sistema:

```bash
sudo apt install python3-pip python3-venv
python3 -m venv ~/promptio-render && source ~/promptio-render/bin/activate
pip install -r renderizador/requirements.txt
playwright install --with-deps chromium
```

`--with-deps` instala las librerías de sistema (fuentes, libnss3, libgbm…)
que Chromium headless necesita y que un VPS mínimo no trae. Sin ellas, el
navegador falla al arrancar con un error poco descriptivo.

**Si el VPS ya tiene Chromium**, no hace falta que Playwright descargue el
suyo: Playwright exige una build exacta y falla si la instalada no coincide.
Apunta al binario existente:

```bash
export PROMPTIO_CHROMIUM=/usr/bin/chromium
```

El renderizador lo busca en este orden: `$PROMPTIO_CHROMIUM`, la build más
nueva bajo `$PLAYWRIGHT_BROWSERS_PATH`, `/usr/bin/chromium`,
`/usr/bin/chromium-browser`, `/usr/bin/google-chrome`, y por último el de
Playwright.

**Recursos**: un render de 6 láminas tarda unos segundos y consume lo que
consuma un Chromium. En un VPS pequeño con n8n ya corriendo, cuenta con
picos de 300–500 MB. El servicio serializa los renders con un cerrojo para
no arrancar varios Chromium a la vez.

**Si n8n corre en Docker**, el contenedor no ve el renderizador del host.
Dos salidas: publicar el servicio en la IP del host y apuntar
`renderizadorUrl` a `http://host.docker.internal:8099`, o meter el
renderizador en su propio contenedor con Chromium dentro. La primera es
menos trabajo.

### 2. Copia del repo en el VPS

El renderizador lee `calendario.md` y `guiones/` **del disco local**, no de
la API de GitHub. Necesitas un clon en el VPS y mantenerlo al día:

```bash
git clone git@github.com:BATCUR/promptio-content.git ~/promptio-content
```

Lo más simple es un `git pull` en un cron a las 08:55, justo antes del
trigger de las 09:00. Si el clon se queda atrás, el renderizador compondrá
la lámina con un guion viejo y nadie se enterará: el post saldría publicado
con el texto anterior.

### 3. El servicio HTTP

```bash
export PROMPTIO_TOKEN="$(openssl rand -hex 24)"
export PROMPTIO_BASE_URL="http://127.0.0.1:8099"
python3 renderizador/servicio.py --puerto 8099
```

Como servicio de systemd, para que sobreviva a reinicios:

```ini
# /etc/systemd/system/promptio-render.service
[Unit]
Description=Renderizador de carruseles PROMPTIO
After=network.target

[Service]
User=promptio
WorkingDirectory=/home/promptio/promptio-content
Environment=PROMPTIO_TOKEN=el-token-que-generaste
Environment=PROMPTIO_BASE_URL=http://127.0.0.1:8099
ExecStart=/home/promptio/promptio-render/bin/python renderizador/servicio.py --puerto 8099
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

El servicio **se niega a arrancar sin `PROMPTIO_TOKEN`**: escribe en disco
y sirve archivos, así que no debe quedar abierto por descuido. Escucha en
`127.0.0.1` por defecto. No lo publiques en internet.

Endpoints:

| Método | Ruta | Para qué |
|--------|------|----------|
| `GET` | `/salud` | Comprobar que está vivo (sin token) |
| `POST` | `/render` | `{"id":"s1p1","modo":"campos"}` → lista de láminas con su URL |
| `GET` | `/laminas/semana-N/<id>/<archivo>.png` | Descargar una lámina |

### 4. Postiz

- API key de los ajustes de Postiz.
- Canal de Instagram conectado a `@promptio_` y su `integration id`:

  ```bash
  curl -H "Authorization: TU_API_KEY" https://postiz.TU-DOMINIO.com/public/v1/integrations
  ```

### 5. Meta Graph API — para el primer comentario

- Cuenta de Instagram profesional vinculada a una página de Facebook.
- App de Meta con Instagram Graph API.
- Permisos `instagram_basic` e `instagram_manage_comments`. Los de gestión
  de comentarios pasan por App Review: **cuenta días, no horas**.
- Token de larga duración, con recordatorio de renovación. Cuando caduque,
  el post se publicará igual y el comentario fallará; solo lo verás en la
  columna `Comentario` del log.
- IG User ID numérico de `@promptio_`.

### 6. GitHub

Fine-grained PAT de `BATCUR` con acceso solo a `promptio-content` y
**Contents: Read and write**.

### 7. Telegram

Bot de BotFather y **chat ID real**, obtenido de
`https://api.telegram.org/bot<TOKEN>/getUpdates` (campo
`result[0].message.chat.id`). Un chat ID inventado falla sin error visible:
el nodo se pone verde y el mensaje no llega.

---

## Importar en n8n

1. n8n → **Import from File** → `workflow-publicacion.json`.
2. Se crea **PROMPTIO — Publicacion automatica (render local + Postiz)**,
   desactivado. Trae `"active": false` a propósito.

n8n no importa credenciales, solo la referencia. Los nodos salen en rojo
hasta que selecciones las tuyas a mano.

### Las cinco credenciales

| Credencial | Tipo en n8n | Valor | Nodos |
|------------|-------------|-------|-------|
| GitHub PROMPTIO | GitHub API | el PAT | 4 |
| Renderizador PROMPTIO | Header Auth | `X-Token` = `PROMPTIO_TOKEN` | 2 |
| Postiz API | Header Auth | `Authorization` = API key, **sin** `Bearer` | 2 |
| Meta Graph API | Header Auth | `Authorization` = `Bearer <token>` | 2 |
| Telegram PROMPTIO | Telegram API | token de BotFather | 4 |

Ojo con los dos `Authorization`: Postiz lo quiere **sin** `Bearer` y Meta
**con**. Es el error de configuración más fácil de cometer aquí.

### Configurar el nodo `Configuracion`

| Campo | Qué poner |
|-------|-----------|
| `owner` / `repo` / `branch` | `BATCUR` / `promptio-content` / `main` |
| `zonaHoraria` | `Europe/Madrid` — verifícalo |
| `renderizadorUrl` | `http://127.0.0.1:8099`, sin barra final |
| `renderizadorModo` | `campos` o `slides` |
| `postizUrl` | Base de Postiz, sin barra final y sin `/public/v1` |
| `postizIntegrationId` | Id del canal de `@promptio_` |
| `igUserId` | IG User ID numérico |
| `metaVersion` | `v21.0` u otra vigente |
| `telegramChatId` | El de `getUpdates` |

---

## Qué tiene que traer el guion

| Campo | Va a |
|-------|------|
| `**Título (autofill):**` | portada del carrusel |
| `**Cita (autofill):**` | lámina de cita (en teal) |
| `**Desarrollo (autofill):**` | láminas de desarrollo |
| `**Slides:**` | láminas, solo en modo `slides` |
| `**Caption:**` | el texto del post en Instagram |
| `**Comentario funcional:**` | el primer comentario |

Sin cualquiera de los cinco primeros, el workflow avisa y no publica.

El comentario funcional debe ser **accionable**: algo que se pueda hacer en
dos minutos al terminar de leer, no una reflexión. El del Post 1 sirve de
referencia.

---

## Probar con el Post 1

1. **Sin n8n, primero.** Genera el carrusel a mano y míralo:

   ```bash
   python3 renderizador/generar_carrusel.py s1p1 --modo slides
   ```

   Compáralo con el post real ya publicado en Instagram. Mira sobre todo:
   tipografía del título, posición del gato y de la línea dorada, y la
   lámina de cierre.

2. **El servicio.** Arráncalo y comprueba la ida y vuelta completa:

   ```bash
   curl -sS http://127.0.0.1:8099/salud
   curl -sS -X POST http://127.0.0.1:8099/render \
        -H "X-Token: $PROMPTIO_TOKEN" -H "Content-Type: application/json" \
        -d '{"id":"s1p1","modo":"slides"}'
   ```

3. **La rama de fallo del workflow.** Vacía temporalmente el campo
   `**Comentario funcional:**` del Post 1, commit, y dale a **Execute
   Workflow**. Debe llegarte el aviso por Telegram y pararse antes de
   renderizar nada. Restaura el campo.

4. **El pipeline completo.** Ejecuta con el post real y vigila que
   `Evaluar render` devuelva tantas URLs como láminas, que Postiz responda
   sin error y que aparezca la fila en `log.md` con `Comentario` en `sí`.

5. **El anti-duplicado.** Vuelve a ejecutar sin cambiar nada: no debe pasar
   nada, porque `s1p1` ya está en el log.

6. Borra de Instagram el post de prueba y su fila del log si no querías
   publicarlo de verdad.

Solo entonces, activa el workflow.

---

## Checklist antes de activar

- [ ] Chromium instalado en el VPS y arrancando (`--with-deps` o
      `PROMPTIO_CHROMIUM` apuntando al binario del sistema)
- [ ] Clon del repo en el VPS, con `git pull` automático antes de las 09:00
- [ ] `promptio-render.service` activo y sobreviviendo a un reinicio
- [ ] `PROMPTIO_TOKEN` generado y puesto también en la credencial de n8n
- [ ] El servicio escuchando en `127.0.0.1`, no expuesto a internet
- [ ] Si n8n va en Docker: `renderizadorUrl` alcanzable desde el contenedor
- [ ] Las cinco credenciales **seleccionadas nodo por nodo**
- [ ] `Authorization` sin `Bearer` en Postiz y con `Bearer` en Meta
- [ ] `instagram_manage_comments` aprobado en App Review, no solo solicitado
- [ ] `telegramChatId` de `getUpdates`, no deducido
- [ ] Tests del renderizador en verde en el VPS, no solo en tu máquina
- [ ] Carrusel del Post 1 comparado a ojo con el publicado en Instagram
- [ ] Prueba de rama de fallo: llega alerta, no se publica
- [ ] Prueba de anti-duplicado: la segunda ejecución no hace nada
- [ ] Versión de n8n comprobada contra
      [las advisories del proyecto](https://github.com/n8n-io/n8n/security/advisories)
- [ ] Workflow guardado explícitamente después del último cambio

---

## Limitaciones conocidas

**El gato es un dibujo nuevo, no el vuestro.** No tengo acceso a las
imágenes publicadas en `@promptio_`, así que `assets/gato.svg` es un line
art original hecho a partir de la descripción. Casi seguro que no coincide
con vuestra mascota. Sustituye ese archivo por el SVG real y no hace falta
tocar nada más: el layout lo coloca igual.

**La tipografía es una suposición razonable.** Anton es la condensada de
Google Fonts más cercana a la descripción, pero no sé cuál usaba la
plantilla de Canva. Si era otra, cambia el archivo en `assets/fonts/` y el
nombre de familia en `plantilla.py`.

**El logo está reconstruido.** El wordmark respeta la regla de color de la
landing (ambas O en teal, la I en dorado) dentro de un aro doble, pero es
una interpretación de "logo circular PROMPTIO". Si tenéis el original en
SVG, sustituye `assets/logo-promptio.svg`.

**Los reels siguen sin cubrir.** El renderizador produce PNG. Las cuatro
piezas de vídeo del calendario se publicarían como carruseles de imágenes.
Publícalos a mano y deja su fila en `log.md` para que el workflow los
ignore.

**Localizar el post para comentar es indirecto.** Postiz no devuelve el
media ID de Instagram, así que el workflow lo busca en el feed comparando
los primeros 60 caracteres del caption entre los medios de los últimos 30
minutos. Si Postiz tarda más de los 3 minutos de espera, el post queda
publicado sin comentario: recibes el texto por Telegram para pegarlo a mano
y el log lo marca con `NO`.

**El objeto `settings` de Postiz va vacío.** Instagram puede exigir claves
propias ahí; el error de validación de la API dice cuáles.

**Seguridad de la instancia.** n8n self-hosted no se parchea solo. Durante
2026 se publicaron varios fallos críticos, incluida ejecución remota de
código sin autenticar. Comprueba tu versión contra las advisories
enlazadas arriba antes de dejar esto corriendo solo. Este workflow guarda
credenciales de cuatro servicios.
