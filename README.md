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
├── README.md        Este archivo
├── calendario.md    Calendario editorial de 4 semanas
└── guiones/         Copy y guiones completos, un archivo por semana
    ├── semana-1.md
    ├── semana-2.md
    ├── semana-3.md
    └── semana-4.md
```

- **`calendario.md`** — la planificación. Cada semana es una sección con
  su rango de fechas (lunes a domingo) y cada post un sub-punto con
  título, formato y ángulo. Es el índice: se edita cuando cambia el plan,
  no cuando se escribe una pieza. Ciclo actual: **3 al 30 de agosto de 2026**.
- **`guiones/`** — la ejecución. Cada archivo de semana arranca vacío y
  se va llenando con el copy final de cada post a medida que se escribe.

## Cómo se trabaja

1. El calendario define el plan de las próximas 4 semanas.
2. Al escribir una pieza, su guion completo se añade al archivo de la
   semana correspondiente en `guiones/`.
3. Un commit por pieza escrita o por bloque de trabajo, con mensaje
   descriptivo (ej. `guiones: semana 1, post 1 (gato y puerta)`).
4. Cuando se cierra un ciclo de 4 semanas, `calendario.md` se reemplaza
   por el siguiente y los guiones quedan como archivo histórico.

## Convenciones

- Todo en español.
- Formatos: `post`, `post corto`, `carrusel`, `carrusel corto`, `reel`.
- Los ejemplos de fallos de IA se escriben en genérico: nunca se expone
  trabajo real de clientes ni de seguidores sin permiso explícito.
