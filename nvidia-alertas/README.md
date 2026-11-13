# 📈 Alertas de Nvidia en el celular

Un robot gratuito que corre en GitHub Actions y manda **notificaciones push** al celular con la app **ntfy**:

| Aviso | Cuándo |
|---|---|
| 📈 / 📉 **NVDA sube / baja X%** | Cada vez que el precio se mueve **2 %** desde el último aviso (en horario de mercado). |
| 🚨 **NVDA ±X% en el día** | Cuando la variación del día cruza **±3 %, ±5 %, ±7 % o ±10 %** (prioridad máxima, suena fuerte). |
| 🔔 **Cierre NVDA** | Resumen al cierre del mercado (18:00 hora Argentina aprox.). |
| 📰 **Noticias** | Cada noticia nueva de Nvidia (Google Noticias en español e inglés + Yahoo Finance). Tocá la notificación para abrirla. |

Revisa cada **10 minutos** con el mercado abierto (lunes a viernes, 11:30–18:00 hora Argentina) y cada hora el resto del tiempo (solo noticias).

## Puesta en marcha (5 minutos)

1. **Instalá ntfy** en el celular: [Android (Play Store)](https://play.google.com/store/apps/details?id=io.heckel.ntfy) · [iPhone (App Store)](https://apps.apple.com/app/ntfy/id1625396347).
2. En la app tocá **+ (Suscribirse a un tema)** y escribí un nombre de tema **difícil de adivinar**, por ejemplo `nvda-german-8k3q7z`. Cualquiera que sepa el nombre puede leerlo, así que no uses algo obvio.
3. En GitHub, en este repositorio: **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `NTFY_TOPIC`
   - Secret: el mismo nombre de tema del paso 2.
4. Hacé que este código quede en la rama **`main`** (GitHub solo corre las tareas programadas desde la rama principal).
5. Probalo: **Actions → Alertas Nvidia → Run workflow → modo `test`**. En unos segundos te llega "✅ Alertas de Nvidia funcionando" con el precio actual.

Listo: desde ahí corre solo.

## Ajustes opcionales

En **Settings → Secrets and variables → Actions → Variables** podés crear:

- `STEP_PCT` – cada cuánto % avisar (por defecto `2`). Con `1` te avisa más seguido.
- `DAILY_LEVELS` – niveles de alerta urgente del día (por defecto `3,5,7,10`).

## A tener en cuenta

- GitHub puede retrasar las tareas programadas unos minutos en horas pico: es un aviso, no un precio en tiempo real al segundo.
- Si el repositorio pasa 60 días sin cambios, GitHub pausa las tareas programadas; se reactivan desde la pestaña Actions.
- El precio sale de Yahoo Finance (con Stooq de respaldo). Esto es información, no una recomendación de inversión.

Probar en la computadora sin enviar nada: `DRY_RUN=1 python nvidia-alertas/alertas.py`
