#!/usr/bin/env python3
"""
Alertas de NVIDIA (NVDA) -> notificaciones push al celular vía ntfy.

- Precio: avisa cuando la acción se mueve STEP_PCT % desde el último aviso
  (sube o baja), y cuando la variación del día cruza niveles clave.
- Resumen: un aviso al cierre del mercado con la variación del día.
- Noticias: avisa de cada noticia nueva de Nvidia (Google News + Yahoo Finance).

Solo usa la biblioteca estándar de Python. El estado (último precio avisado,
noticias ya vistas) se guarda en un JSON que el workflow conserva entre corridas.
"""

import email.utils
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# ----------------------------- Configuración -----------------------------
TICKER = os.environ.get("TICKER", "NVDA")
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
# Avisar cada vez que el precio se mueva este % desde el último aviso.
STEP_PCT = float(os.environ.get("STEP_PCT", "2"))
# Niveles de variación diaria (vs. cierre anterior) que generan un aviso urgente.
DAILY_LEVELS = [float(x) for x in os.environ.get("DAILY_LEVELS", "3,5,7,10").split(",") if x.strip()]
MAX_NEWS_PER_RUN = int(os.environ.get("MAX_NEWS_PER_RUN", "5"))
NEWS_MAX_AGE_HOURS = int(os.environ.get("NEWS_MAX_AGE_HOURS", "24"))
LOCAL_TZ = ZoneInfo(os.environ.get("LOCAL_TZ", "America/Argentina/Buenos_Aires"))
STATE_FILE = os.environ.get("STATE_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json"))
DRY_RUN = os.environ.get("DRY_RUN") == "1"  # imprime en vez de enviar

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

NEWS_FEEDS = [
    "https://news.google.com/rss/search?q=Nvidia+when:1d&hl=es-419&gl=AR&ceid=AR:es-419",
    "https://news.google.com/rss/search?q=Nvidia+OR+NVDA+when:1d&hl=en-US&gl=US&ceid=US:en",
    f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={TICKER}&region=US&lang=en-US",
]


# ------------------------------- Utilidades -------------------------------
def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def notify(title, message, tags=None, priority=3, click=None):
    """Envía una notificación push a ntfy (formato JSON, admite acentos y emojis)."""
    payload = {"topic": NTFY_TOPIC, "title": title, "message": message, "priority": priority}
    if tags:
        payload["tags"] = tags
    if click:
        payload["click"] = click
    if DRY_RUN or not NTFY_TOPIC:
        print(f"[NOTIF p{priority}] {title}\n  {message}\n  tags={tags} click={click}")
        return
    req = urllib.request.Request(
        NTFY_SERVER,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "nvidia-alertas"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()
    print(f"Enviada: {title}")


def fmt_pct(x):
    return f"{x:+.2f}%".replace(".", ",")


def fmt_usd(x):
    return f"US$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --------------------------------- Precio ---------------------------------
def quote_yahoo():
    last_err = None
    for host in ("query1", "query2"):
        try:
            url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{TICKER}?interval=5m&range=1d"
            meta = json.loads(http_get(url))["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice")
            prev = meta.get("chartPreviousClose") or meta.get("previousClose")
            if price is None or not prev:
                raise ValueError("respuesta sin precio")
            period = (meta.get("currentTradingPeriod") or {}).get("regular") or {}
            return {
                "price": float(price),
                "prev_close": float(prev),
                "market_time": int(meta.get("regularMarketTime") or 0),
                "open_ts": int(period.get("start") or 0),
                "close_ts": int(period.get("end") or 0),
                "source": "Yahoo",
            }
        except Exception as e:  # noqa: BLE001
            last_err = e
    raise RuntimeError(f"Yahoo falló: {last_err}")


def quote_stooq():
    """Respaldo: Stooq (último precio + cierre anterior del histórico diario)."""
    sym = f"{TICKER.lower()}.us"
    rows = http_get(f"https://stooq.com/q/d/l/?s={sym}&i=d").decode().strip().splitlines()
    closes = [r.split(",") for r in rows[1:] if r.count(",") >= 4]
    live = http_get(f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv").decode().strip().splitlines()
    cols = dict(zip(live[0].split(","), live[1].split(",")))
    price = float(cols["Close"])
    today = cols["Date"]
    prev = next(float(r[4]) for r in reversed(closes) if r[0] != today)
    return {"price": price, "prev_close": prev, "market_time": 0, "open_ts": 0, "close_ts": 0, "source": "Stooq"}


def get_quote():
    try:
        return quote_yahoo()
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: {e}. Probando Stooq...", file=sys.stderr)
        return quote_stooq()


def market_open(q, now_ts):
    if q["open_ts"] and q["close_ts"]:
        return q["open_ts"] <= now_ts < q["close_ts"]
    # Sin datos de horario: lunes a viernes 9:30–16:00 Nueva York.
    ny = datetime.fromtimestamp(now_ts, ZoneInfo("America/New_York"))
    mins = ny.hour * 60 + ny.minute
    return ny.weekday() < 5 and 570 <= mins < 960


def check_price(state, now_ts):
    q = get_quote()
    price, prev = q["price"], q["prev_close"]
    day_pct = (price / prev - 1) * 100
    trading_day = datetime.fromtimestamp(q["market_time"] or now_ts, ZoneInfo("America/New_York")).date().isoformat()
    ps = state.setdefault("price", {})
    is_open = market_open(q, now_ts)
    link = f"https://finance.yahoo.com/quote/{TICKER}"
    print(f"{TICKER} {price:.2f} (cierre ant. {prev:.2f}, {day_pct:+.2f}%) fuente={q['source']} abierto={is_open}")

    # Nuevo día de mercado: el punto de referencia pasa a ser el cierre anterior.
    if ps.get("day") != trading_day:
        ps.update({"day": trading_day, "ref": prev, "levels": [], "closed_sent": False})

    if is_open:
        move = (price / ps["ref"] - 1) * 100
        sign = "+" if day_pct > 0 else "-"
        # 1) Variación diaria que cruza un nivel clave (±3, ±5, ...): aviso urgente.
        crossed = [l for l in DAILY_LEVELS if abs(day_pct) >= l and f"{sign}{l:g}" not in ps["levels"]]
        if crossed:
            ps["levels"] += [f"{sign}{l:g}" for l in crossed]
            notify(
                f"🚨 NVDA {fmt_pct(day_pct)} en el día",
                f"Superó el {sign}{max(crossed):g}% hoy.\nPrecio: {fmt_usd(price)} "
                f"(cierre anterior {fmt_usd(prev)})\nDesde el último aviso: {fmt_pct(move)}",
                tags=["rotating_light"],
                priority=5,
                click=link,
            )
            ps["ref"] = price
        # 2) Movimiento de STEP_PCT % desde el último aviso (sube o baja).
        elif abs(move) >= STEP_PCT:
            up = move > 0
            notify(
                f"{'📈 NVDA sube' if up else '📉 NVDA baja'} {fmt_pct(move)}",
                f"Precio: {fmt_usd(price)}\nDesde el último aviso: {fmt_pct(move)} ({fmt_usd(ps['ref'])})\n"
                f"En el día: {fmt_pct(day_pct)}",
                tags=["chart_with_upwards_trend" if up else "chart_with_downwards_trend"],
                priority=4,
                click=link,
            )
            ps["ref"] = price
    elif q["close_ts"] and now_ts >= q["close_ts"] and not ps.get("closed_sent") and q["market_time"] >= q["open_ts"] > 0:
        # 3) Resumen al cierre.
        notify(
            f"🔔 Cierre NVDA: {fmt_pct(day_pct)}",
            f"Cerró en {fmt_usd(price)} (anterior {fmt_usd(prev)}).",
            tags=["bell"],
            priority=3,
            click=link,
        )
        ps["closed_sent"] = True
    return q


# -------------------------------- Noticias --------------------------------
def parse_feed(xml_bytes):
    items = []
    root = ET.fromstring(xml_bytes)
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src_el = it.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        pub = it.findtext("pubDate")
        try:
            pub_dt = email.utils.parsedate_to_datetime(pub) if pub else None
        except (TypeError, ValueError):
            pub_dt = None
        if source and title.endswith(f" - {source}"):
            title = title[: -len(source) - 3].strip()
        if title:
            items.append({"title": title, "link": link, "source": source, "pub": pub_dt})
    return items


def news_key(title):
    norm = re.sub(r"[^a-z0-9áéíóúñü]+", " ", title.lower()).strip()
    return hashlib.sha1(norm.encode()).hexdigest()[:16]


def check_news(state, now):
    seen = state.setdefault("news_seen", {})
    first_run = not seen
    fresh = []
    for url in NEWS_FEEDS:
        try:
            items = parse_feed(http_get(url))
        except Exception as e:  # noqa: BLE001
            print(f"Aviso: feed falló ({urllib.parse.urlparse(url).netloc}): {e}", file=sys.stderr)
            continue
        for it in items:
            k = news_key(it["title"])
            if k in seen:
                continue
            seen[k] = now.isoformat()
            if it["pub"] and now - it["pub"] > timedelta(hours=NEWS_MAX_AGE_HOURS):
                continue
            if not re.search(r"nvidia|nvda|jensen huang", it["title"], re.I):
                continue
            fresh.append(it)

    # Limpia noticias vistas hace más de 7 días.
    cutoff = now - timedelta(days=7)
    for k, v in list(seen.items()):
        try:
            if datetime.fromisoformat(v) < cutoff:
                del seen[k]
        except ValueError:
            del seen[k]

    if first_run:
        print(f"Primera corrida: {len(fresh)} noticias marcadas como vistas (sin avisar).")
        return 0

    fresh.sort(key=lambda x: x["pub"] or now, reverse=True)
    for it in fresh[:MAX_NEWS_PER_RUN]:
        when = it["pub"].astimezone(LOCAL_TZ).strftime("%d/%m %H:%M") if it["pub"] else ""
        notify(
            f"📰 {it['source'] or 'Noticia'} · Nvidia",
            f"{it['title']}\n{when}".strip(),
            tags=["newspaper"],
            priority=3,
            click=it["link"] or None,
        )
    if len(fresh) > MAX_NEWS_PER_RUN:
        notify(
            "📰 Más noticias de Nvidia",
            f"Hay {len(fresh) - MAX_NEWS_PER_RUN} noticias más. Tocá para verlas.",
            tags=["newspaper"],
            priority=2,
            click="https://news.google.com/search?q=Nvidia&hl=es-419&gl=AR&ceid=AR:es-419",
        )
    return len(fresh)


# ---------------------------------- Main ----------------------------------
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if not NTFY_TOPIC and not DRY_RUN:
        sys.exit("Falta NTFY_TOPIC (configuralo como secret en GitHub).")

    now = datetime.now(timezone.utc)
    if mode == "test":
        try:
            q = get_quote()
            body = f"NVDA ahora: {fmt_usd(q['price'])} ({fmt_pct((q['price'] / q['prev_close'] - 1) * 100)} en el día)."
        except Exception as e:  # noqa: BLE001
            body = f"No pude leer el precio: {e}"
        notify("✅ Alertas de Nvidia funcionando", body, tags=["white_check_mark"], priority=4)
        return

    state = load_state()
    errors = []
    try:
        check_price(state, int(now.timestamp()))
    except Exception as e:  # noqa: BLE001
        errors.append(f"precio: {e}")
    try:
        check_news(state, now)
    except Exception as e:  # noqa: BLE001
        errors.append(f"noticias: {e}")
    state["last_run"] = now.isoformat()
    save_state(state)
    if errors:
        print("Errores: " + "; ".join(errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
