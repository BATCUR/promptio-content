# Calendario de contenido — 3 al 30 de agosto de 2026

Plan editorial de PROMPTIO para el próximo ciclo de 4 semanas. Cada
semana va de lunes a domingo.

Cada post lleva un identificador y su fecha/hora de publicación:

```
- **Título** · *formato* · `id` · `AAAA-MM-DD HH:MM`
```

Ese formato lo lee el workflow de n8n (`workflow-publicacion.json`) para
saber qué toca publicar cada día, así que **la estructura de esas líneas
no se puede romper**: cambia los valores, no los backticks ni los `·`.
El `id` (`s1p1` = semana 1, post 1; `s1r1` = semana 1, reel 1) es la
clave que conecta las tres piezas de un post:

| Dónde | Ruta |
|-------|------|
| Guion | `guiones/semana-1.md`, encabezado que termina en `· s1p1` |
| Visual | `imagenes/semana-1/s1p1.png` (o `s1p1-01.png`, `s1p1-02.png`… en carrusel) |
| Registro | fila `s1p1` en `log.md` |

Las horas están en la zona horaria configurada en el workflow
(`Europe/Madrid` por defecto).

---

## Semana 1 — 3 al 9 de agosto — El problema base (por qué falla instruir mal)

- **Post 1 — La escena del gato y la puerta** · *carrusel* · `s1p1` · `2026-08-03 18:30`
  Instrucción incompleta vs. desobediencia: el gato no te desobedece, es
  que nunca le dijiste lo que querías. Ancla la tesis de la marca en una
  imagen concreta antes de hablar de IA.

- **Post 2 — "El error #1"** · *carrusel* · `s1p2` · `2026-08-05 18:30`
  Mismo formato ya validado en la cuenta. Se reutiliza la estructura que
  funcionó para instalar el diagnóstico central.

- **Post 3 — Por qué "sé más específico" no es un consejo útil** · *carrusel corto* · `s1p3` · `2026-08-07 18:30`
  Ataca el consejo vacío que todo el mundo repite y define qué significa
  especificidad real: qué información concreta falta, no "más palabras".

- **Reel — Vaga vs. clara** · *reel* · `s1r1` · `2026-08-08 20:00`
  Instrucción vaga vs. instrucción clara: mismo objetivo, resultado
  distinto. Demostración visual rápida del problema de la semana.

---

## Semana 2 — 10 al 16 de agosto — El framework de 5 partes

- **Post 1 — Rol** · *carrusel* · `s2p1` · `2026-08-10 18:30`
  Qué es y por qué la IA responde distinto según a quién le pides que
  actúe. Primera pieza del framework.

- **Post 2 — Tarea + Contexto/Audiencia** · *carrusel* · `s2p2` · `2026-08-11 18:30`
  La diferencia entre pedir algo y pedirlo para alguien específico. El
  contexto no es adorno: cambia la respuesta.

- **Post 3 — Restricciones** · *carrusel* · `s2p3` · `2026-08-13 18:30`
  Por qué "sin restricciones" da resultados genéricos. Limitar es dirigir.

- **Post 4 — Few-Shot** · *carrusel* · `s2p4` · `2026-08-14 18:30`
  Mostrar un ejemplo vale más que explicar con palabras. Cierra el
  framework con la pieza más subestimada.

- **Reel — Las 5 partes en 30 segundos** · *reel* · `s2r1` · `2026-08-16 20:00`
  Versión reel del mismo contenido, condensada para alcance.

---

## Semana 3 — 17 al 23 de agosto — Aplicación cruzada de plataformas

- **Post 1 — El framework en Gemini** · *carrusel* · `s3p1` · `2026-08-17 18:30`
  El framework de la Semana 2 aplicado paso a paso en Gemini.

- **Post 2 — El framework en ChatGPT** · *carrusel* · `s3p2` · `2026-08-19 18:30`
  El mismo framework, la misma estructura, otra plataforma. Demuestra que
  la habilidad es transferible, no un truco de una herramienta.

- **Post 3 — Qué es un "skill"** · *carrusel* · `s3p3` · `2026-08-21 18:30`
  Una instrucción bien estructurada con memoria. Se conecta explícitamente
  con el framework: un skill no es magia, es el framework guardado.

- **Reel — Mismo prompt, 2 plataformas** · *reel* · `s3r1` · `2026-08-23 20:00`
  Con y sin framework, resultado comparado lado a lado.

---

## Semana 4 — 24 al 30 de agosto — Cuando la IA falla + anticipación

- **Post 1 — Un caso de falla por instrucción incompleta** · *carrusel* · `s4p1` · `2026-08-24 18:30`
  Caso genérico, sin exponer trabajo real del usuario. Muestra el costo
  concreto de instruir mal.

- **Post 2 — El factor humano** · *carrusel* · `s4p2` · `2026-08-26 18:30`
  Por qué el problema nunca es solo la máquina. Puente hacia la segunda
  mitad del título del libro: *(y a ti mismo)*.

- **Post 3 — "Llevamos un mes documentando esto"** · *post corto* · `s4p3` · `2026-08-28 18:30`
  Guiño de que viene algo más grande, sin revelar el libro todavía.

- **Post final — Anuncio del libro** · *reel* · `s4r1` · `2026-08-30 20:00`
  Anuncio de *PROMPTIO — El arte de instruir a una máquina (y a ti mismo)*
  con el rebranding visual planeado.
