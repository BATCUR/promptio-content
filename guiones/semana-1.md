# Guiones — Semana 1 · 3 al 9 de agosto

*El problema base (por qué falla instruir mal)*

Copy y guiones completos de las piezas de esta semana. Ver el plan en
[`../calendario.md`](../calendario.md).

El identificador del encabezado (`s1p1`) es lo que usa el workflow de n8n
para encontrar este guion. Los campos marcados **(autofill)** los lee el
renderizador local (`renderizador/`) para componer las láminas: si cambias
su nombre aquí, deja de encontrarlos.

Lo que **no** se escribe en estos guiones, porque lo pone el renderizador
y no varía nunca: la lámina de cierre ("La claridad en tu instrucción
determina la calidad del resultado." + logo PROMPTIO), y la posición del
gato y de la línea dorada en la portada.

---

## Post 1 — La escena del gato y la puerta · carrusel · s1p1

**Estado:** listo

**Título (autofill):**
CIERRA LA PUERTA

**Cita (autofill):**
Hizo exactamente lo que dijiste. No lo que querías.

**Desarrollo (autofill):**
Le pides a alguien que cierre la puerta. La cierra. El gato se queda
fuera. No fue desobediencia: la instrucción estaba incompleta desde el
principio. Con una IA pasa lo mismo, solo que más rápido.

**Slides:**

*Slide 1 — Portada*
> # CIERRA LA PUERTA

*Slide 2 — La escena*
> Le pides a alguien que cierre la puerta.
>
> La cierra.
>
> El gato se queda fuera.

*Slide 3 — El giro*
> Tu primera reacción es pensar que hizo algo mal.
>
> No hizo nada mal.
>
> Hizo exactamente lo que dijiste.

*Slide 4 — La conexión con IA*
> Con una IA pasa lo mismo, más rápido.
>
> Le pides algo sin el contexto completo y te devuelve lo que pediste,
> no lo que querías.
>
> Y como responde en tres segundos, parece que el fallo es suyo.

*Slide 5 — La regla de fondo*
> La claridad de una instrucción es responsabilidad de quien la da.
>
> No de quien la ejecuta.
>
> Da igual que sea una persona o una máquina.

*Slide 6 — Cierre*
> Lámina fija de marca. La añade el renderizador, no se escribe aquí.

**Caption:**
Le pediste que cerrara la puerta. La cerró. El gato se quedó fuera.

Y durante un segundo piensas que hizo algo mal.

No hizo nada mal. Hizo exactamente lo que dijiste. Lo que pasa es que lo
que dijiste y lo que querías no eran la misma cosa. En tu cabeza la
instrucción era "cierra la puerta cuando el gato ya esté dentro". En voz
alta fueron cuatro palabras.

Esto es lo que ocurre cada vez que le pides algo a una IA y el resultado
te deja frío.

❌ "Escríbeme un post sobre productividad" → te devuelve algo que podría
haber escrito cualquiera, sobre cualquier cosa, para nadie en particular.

✅ "Escribe un post para gente que trabaja sola y siente que pierde el día
en tareas pequeñas. Tono directo, sin frases motivacionales, máximo 120
palabras" → ahora sí tiene con qué trabajar.

No es que la segunda versión sea más larga. Es que la primera dejaba fuera
todo lo que tú ya dabas por supuesto.

Lo incómodo del asunto: la instrucción incompleta nunca se nota mientras
la escribes. Se nota cuando ves el resultado. Y para entonces la puerta ya
está cerrada.

📌 Guarda este post — vamos a construir sobre esta idea toda la semana.

#Prompts #InteligenciaArtificial #Productividad #IA

**Comentario funcional:**
Para aplicarlo hoy, en dos minutos: abre el último prompt que escribiste y
añádele estas tres líneas antes de volver a enviarlo.

1. Para quién es → "esto lo va a leer ___"
2. Qué no quieres → "evita ___"
3. Cómo sabrás que está bien → "funciona si ___"

Lanza los dos, el viejo y el nuevo, y compara los resultados uno al lado
del otro. La diferencia es la instrucción, no el modelo.

**CTA:**
Guardar el post. Sin enlace externo todavía: esta semana es de instalar la
idea, no de convertir.

**Especificaciones visuales:**
- 6 slides, formato 1080 × 1350 px.
- Tipografía condensada, mayúsculas, en azul marino `#1C2B45` sobre fondo
  crema `#F4EEDD` (paleta de la landing).
- Acentos en dorado `#D9A441` y verde azulado `#3E8C86`.
- Gato y línea dorada en portada: posición fija en `renderizador/marca.py`,
  no se reposicionan por post.
- Última lámina: cierre fijo de marca, lo añade el renderizador.

---

## Post 2 — "El error #1" · carrusel · s1p2

Estado: listo

Título (autofill):

EL ERROR #1

Cita (autofill):

Le describiste el formato. Nunca le dijiste para qué era.

Desarrollo (autofill):

Le pides a una IA que "haga un resumen de tres líneas". Te lo da. Perfecto en

forma, inútil en la práctica: no sabía si era para un jefe, para redes o

para ti mismo dentro de un mes. El error más común no es pedir poco: es

describir el formato y omitir el objetivo.

Slides:

Slide 1 — Portada

> # EL ERROR #1

Slide 2 — La escena

> "Hazme un resumen de tres líneas."

>

> Te lo da. Tres líneas, bien escritas.

>

> Y aun así no sirve.

Slide 3 — El giro

> No fallo el formato.

>

> Fallaste el objetivo: nunca dijiste para qué era ese resumen.

>

> La IA no puede optimizar una meta que no le diste.

Slide 4 — La conexión con IA

> "Tres líneas" es una restricción de forma.

>

> "Para que mi jefe decida en 10 segundos si aprobar el gasto" es un

> objetivo.

>

> Con la primera, adivina. Con la segunda, apunta.

Slide 5 — La regla de fondo

> Antes de decir cómo lo quieres, di para qué es.

>

> El formato se ajusta después. El objetivo es lo que dirige todo lo

> demás.

Slide 6 — Cierre

> Lámina fija de marca. La añade el renderizador, no se escribe aquí.

Caption:

Le pediste un resumen de tres líneas. Te lo dio. Perfecto en forma,

inútil en la práctica.

El problema no fue la extensión. Fue que nunca dijiste para qué era ese

resumen.

Este es el error #1 al instruir una IA: describir el formato y saltarte

el objetivo. "Hazlo corto" es una restricción. "Corto porque mi jefe

decide en 10 segundos si aprobar el gasto" es un objetivo — y son dos

prompts completamente distintos aunque suenen parecidos.

❌ "Resume esto en tres líneas" → optimiza para caber en tres líneas,

nada más.

✅ "Resume esto para que alguien sin contexto previo decida en 10

segundos si aprobar el gasto" → optimiza para la decisión, y el largo

sale solo.

El formato es la parte fácil. El objetivo es la que casi nadie escribe,

y es la que realmente dirige el resultado.

📌 Guarda este post — la próxima pieza de la semana ataca el consejo

contrario: por qué "sé más específico" tampoco es suficiente.

#Prompts #InteligenciaArtificial #Productividad #IA

Comentario funcional:

Prueba esto con el próximo prompt que escribas: antes de describir el

formato (largo, tono, estructura), escribe una frase que empiece con

"Esto es para que ___ pueda ___". Si no puedes completarla, todavía no

tienes objetivo — tienes solo forma.

CTA:

Guardar el post. Sin enlace externo todavía — misma regla que el Post 1.

Especificaciones visuales:

Mismas que el Post 1: 6 slides, 1080×1350, tipografía condensada en

mayúsculas, navy #1C2B45 sobre crema #F4EEDD, acentos dorado #D9A441 y

teal #3E8C86. Gato y línea dorada en posición fija — no se ajustan por

post. Cierre fijo lo añade el renderizador.

---

## Post 3 — Por qué "sé más específico" no es un consejo útil · carrusel corto · s1p3

**Estado:** pendiente

**Título (autofill):**

**Cita (autofill):**

**Desarrollo (autofill):**

**Slides:**

**Caption:**

**Comentario funcional:**

**CTA:**

**Especificaciones visuales:**

---

## Reel — Vaga vs. clara · reel · s1r1

**Estado:** pendiente

**Título (autofill):**

**Cita (autofill):**

**Desarrollo (autofill):**

**Guion / voz en off:**

**Notas de grabación y texto en pantalla:**

**Caption:**

**Comentario funcional:**

**CTA:**

**Especificaciones visuales:**
