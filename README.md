# promptio-content

Repositorio de contenido de la marca **PROMPTIO**.

Aquí vive la planificación editorial y los guiones de todo lo que se
publica en la cuenta: qué se publica, en qué formato, con qué ángulo, y
el copy final de cada pieza.

## Sobre PROMPTIO

PROMPTIO enseña a pensar claro para hablar con IA (y con las personas).
La tesis: la mayoría de los malos resultados con IA no son un fallo del
modelo, son un fallo de instrucción — y aprender a instruir bien a una
máquina te obliga a ordenar tu propio pensamiento.

- **Instagram:** [@promptio_](https://www.instagram.com/promptio_/)
- **Landing / lista de espera:** [dainty-brigadeiros-6061e2.netlify.app](https://dainty-brigadeiros-6061e2.netlify.app)
- **Libro:** *PROMPTIO — El arte de instruir a una máquina (y a ti mismo)*

El contenido de este repo funciona como laboratorio público del libro:
las ideas se prueban primero en formato corto (carrusel, reel, post) y
lo que conecta con la audiencia alimenta el manuscrito.

## Estructura

```
promptio-content/
├── README.md                    Este archivo
├── calendario.md                Calendario editorial de 4 semanas
├── guiones/                     Copy y guiones completos, un archivo por semana
│   ├── semana-1.md
│   ├── semana-2.md
│   ├── semana-3.md
│   └── semana-4.md
├── renderizador/                Genera los carruseles en PNG (Chromium headless)
├── imagenes/                    Salida del renderizador, una carpeta por semana
├── workflow-publicacion.json    Workflow de n8n: render → Postiz → comentario
├── README-automatizacion.md     Cómo importarlo, configurarlo y probarlo
└── log.md                       Registro de lo ya programado (lo escribe n8n)
```

- **`calendario.md`** — la planificación. Cada semana es una sección con
  su rango de fechas (lunes a domingo) y cada post un sub-punto con
  título, formato y ángulo. Es el índice: se edita cuando cambia el plan,
  no cuando se escribe una pieza. Ciclo actual: **3 al 30 de agosto de 2026**.
- **`guiones/`** — la ejecución. Cada archivo de semana arranca vacío y
  se va llenando con el copy final de cada post a medida que se escribe.
- **`workflow-publicacion.json`** — la automatización. Ver
  [`README-automatizacion.md`](./README-automatizacion.md).

Todo se enlaza por el **id** del post (`s1p1` = semana 1, post 1), que se
define en `calendario.md` y se repite en el encabezado del guion y en la
fila del log.

Los visuales los genera el renderizador local a partir de los campos
`(autofill)` del guion, sin pasar por ningún servicio externo:

```bash
python3 renderizador/generar_carrusel.py s1p1 --modo slides
```

## Cómo se trabaja

1. El calendario define el plan de las próximas 4 semanas.
2. Al escribir una pieza, su guion completo se añade al archivo de la
   semana correspondiente en `guiones/`.
3. Cada guion tiene que traer sus campos `(autofill)` —título, cita,
   desarrollo—, el caption completo y el comentario funcional. Sin eso el
   workflow no publica.
4. Un commit por pieza escrita o por bloque de trabajo, con mensaje
   descriptivo (ej. `Guion completo: Post 1 - Cierra la puerta`).
5. Cuando se cierra un ciclo de 4 semanas, `calendario.md` se reemplaza
   por el siguiente y los guiones quedan como archivo histórico.

El workflow de n8n corre solo a las 09:00: renderiza el carrusel en el
propio VPS, lo publica en `@promptio_` vía Postiz y añade el primer
comentario. Si algo falla en cualquier punto, avisa por Telegram y no
publica nada.

## Convenciones

- Todo en español.
- Formatos: `post`, `post corto`, `carrusel`, `carrusel corto`, `reel`.
- Los ejemplos de fallos de IA se escriben en genérico: nunca se expone
  trabajo real de clientes ni de seguidores sin permiso explícito.
