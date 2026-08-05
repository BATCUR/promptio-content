# Log de publicaciones — PROMPTIO

Registro del proceso de automatización (Make.com + GitHub Actions).

El proceso **lee este archivo antes de publicar** para no publicar dos
veces el mismo post. Si borras una fila, esa pieza se volverá a publicar
la próxima vez que el trigger corra en su fecha. Es la forma prevista de
reprogramar algo: borrar su fila.

Solo cuentan las filas de la tabla: el anti-duplicado lee la primera
celda de cada fila, no el texto de alrededor. La columna **Comentario**
dice si el primer comentario funcional llegó a publicarse; si pone `NO`,
hay que añadirlo a mano (el texto va en el guion del post).

| ID | Post | Publicado | Láminas | Media ID | Comentario |
|----|------|-----------|---------|----------|------------|
| s1p1 | Cierra la puerta | 2026-08 (manual, Canva) | 4 | desconocido (publicado fuera de Make) | Sí |
