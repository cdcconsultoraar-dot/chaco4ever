# Actualización automática diaria (GitHub Actions)

Con esto, **todos los días a las 9:00 (hora Argentina)** GitHub actualiza solo la
tabla de la Zona A en los 3 paneles y publica el cambio. Como Netlify está
conectado al repo, `chaco4ever.netlify.app` queda al día **sin que tengas que
prender la compu ni pedírmelo**.

Corre en los servidores de GitHub (gratis para repos públicos). Actualiza:
posiciones, PJ/G/E/P/GF/GC/DG/Pts, la columna **Últimos 5**, la posición de For
Ever, el badge (dentro/fuera de la zona) y la fecha de actualización. Los textos
de análisis (destacado, escenarios) quedan como están (son editoriales).

Fuente de datos: la clasificación pública de BeSoccer (Zona A).

---

## Archivos que hacen la magia (ya están en tu carpeta)

- `scripts/update_panel.py` — baja la tabla y actualiza los 3 HTML. Es *fail-safe*:
  si no logra leer las 18 filas o algo no cierra, **no toca nada** (nunca publica
  datos rotos).
- `.github/workflows/actualizar-panel.yml` — el reloj: dispara el script cada día
  a las 12:00 UTC (= 09:00 en Argentina) y publica si hubo cambios.

---

## Puesta en marcha (una sola vez)

**1) Subí estos archivos al repo.**
La forma más simple es doble clic en **`PUBLICAR_TODO.bat`** (te lo dejé en la
carpeta): sube todo, incluidos `scripts/` y `.github/`. También sirve el MCP
`chaco-deploy` o subirlos a mano por la web de GitHub.

**2) Dale permiso de escritura a Actions.**
En GitHub: repo **chaco4ever** → **Settings** → **Actions** → **General** →
abajo, en *Workflow permissions*, elegí **Read and write permissions** → **Save**.

**3) (Opcional) Probalo ya mismo sin esperar a mañana.**
En GitHub: pestaña **Actions** → workflow *"Actualizar panel Chaco For Ever"* →
botón **Run workflow**. En un minuto vas a ver si corrió bien (tilde verde) y,
si hubo cambios, un commit nuevo "Auto: actualizacion diaria...".

¡Listo! De ahí en más se actualiza solo cada mañana.

---

## Cómo saber que está funcionando

- Pestaña **Actions**: cada día debería aparecer una corrida con tilde verde.
- Si ese día hubo partidos, vas a ver un commit "Auto: actualizacion diaria...".
- Si no hubo cambios en la tabla, la corrida dice "Sin cambios" y no publica (normal).

## Notas honestas

- No pude probar la *descarga* de la web desde mi entorno (restricciones de red),
  así que la **primera corrida manual (paso 3) es la prueba de fuego**. Si la
  estructura de la página de BeSoccer fuera distinta a la esperada, el script se
  frena solo sin romper nada y me pasás el log de Actions para ajustarlo.
- La columna *Últimos 5* se actualiza si la web la expone como texto; si la
  publican como iconos, esos círculos podrían quedar en su último valor hasta un
  repaso manual (los números y posiciones sí se actualizan igual).
- El horario de GitHub Actions puede correrse algunos minutos; no es un reloj exacto.
