import os
import requests
from datetime import datetime, timedelta
import schedule
import time
import pytz

# ─── CONFIGURACIÓN ────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SHOPIFY_STORE    = os.environ["SHOPIFY_STORE"]       # ej: soulcute.myshopify.com
SHOPIFY_TOKEN    = os.environ["SHOPIFY_TOKEN"]       # Admin API Access Token

META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
META_AD_ACCOUNT   = os.environ["META_AD_ACCOUNT"]   # ej: act_1112157504418218

TIMEZONE = pytz.timezone("America/Santiago")

# ─── TELEGRAM ─────────────────────────────────────────────────────
def send_telegram(mensaje: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    })

# ─── SHOPIFY: CARROS ABANDONADOS ──────────────────────────────────
def reporte_carros_abandonados():
    try:
        ayer = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime("%Y-%m-%d")
        hoy  = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

        url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/checkouts.json"
        headers = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}
        params  = {
            "created_at_min": f"{ayer}T00:00:00-04:00",
            "created_at_max": f"{hoy}T07:00:00-04:00",
            "limit": 50
        }

        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        checkouts = data.get("checkouts", [])

        if not checkouts:
            send_telegram("🛒 <b>Carros Abandonados — Hoy</b>\n\nNo hubo carros abandonados en las últimas 24h. ✅")
            return

        total_valor = sum(float(c.get("total_price", 0)) for c in checkouts)
        lineas = []

        for c in checkouts:
            nombre  = f"{c.get('billing_address', {}).get('first_name', '')} {c.get('billing_address', {}).get('last_name', '')}".strip()
            if not nombre:
                nombre = c.get("email", "Sin nombre")
            telefono = c.get("billing_address", {}).get("phone", "") or c.get("shipping_address", {}).get("phone", "Sin teléfono")
            email    = c.get("email", "Sin email")
            total    = float(c.get("total_price", 0))
            productos = ", ".join([li["title"] for li in c.get("line_items", [])])
            url_rec  = c.get("abandoned_checkout_url", "")

            lineas.append(
                f"👤 <b>{nombre}</b>\n"
                f"📱 {telefono}\n"
                f"📧 {email}\n"
                f"💰 ${total:,.0f} CLP\n"
                f"🛍️ {productos}\n"
                f"🔗 <a href='{url_rec}'>Link recuperación</a>\n"
                f"{'─'*28}"
            )

        encabezado = (
            f"🛒 <b>CARROS ABANDONADOS — {hoy}</b>\n"
            f"Total: <b>{len(checkouts)} carros</b> | ${total_valor:,.0f} CLP en riesgo\n"
            f"{'═'*28}\n\n"
        )

        # Telegram tiene límite de 4096 chars, dividir si es necesario
        mensaje_completo = encabezado + "\n".join(lineas)
        if len(mensaje_completo) > 4000:
            send_telegram(encabezado + f"(Hay {len(checkouts)} carros — enviando en partes)")
            for i in range(0, len(lineas), 5):
                send_telegram("\n".join(lineas[i:i+5]))
        else:
            send_telegram(mensaje_completo)

    except Exception as e:
        send_telegram(f"⚠️ Error al obtener carros abandonados:\n{str(e)}")

# ─── META ADS: REPORTE DIARIO ─────────────────────────────────────
def reporte_meta_ads():
    try:
        url = f"https://graph.facebook.com/v19.0/{META_AD_ACCOUNT}/insights"
        params = {
            "access_token": META_ACCESS_TOKEN,
            "date_preset": "yesterday",
            "fields": "spend,impressions,clicks,ctr,cpc,actions,cost_per_action_type,purchase_roas",
            "level": "account"
        }

        resp = requests.get(url, params=params)
        data = resp.json()

        if "error" in data:
            send_telegram(f"⚠️ Error Meta Ads API:\n{data['error']['message']}")
            return

        if not data.get("data"):
            send_telegram("📊 <b>Meta Ads — Ayer</b>\n\nSin datos para ayer (puede que no haya habido gasto activo).")
            return

        d = data["data"][0]
        gasto       = float(d.get("spend", 0))
        impresiones = int(d.get("impressions", 0))
        clicks      = int(d.get("clicks", 0))
        ctr         = float(d.get("ctr", 0))
        cpc         = float(d.get("cpc", 0))

        # Extraer compras de actions
        compras = 0
        costo_compra = 0.0
        for action in d.get("actions", []):
            if action["action_type"] == "purchase":
                compras = int(float(action["value"]))
        for cp in d.get("cost_per_action_type", []):
            if cp["action_type"] == "purchase":
                costo_compra = float(cp["value"])

        # ROAS
        roas_list = d.get("purchase_roas", [])
        roas = float(roas_list[0]["value"]) if roas_list else 0.0

        # Semáforo ROAS
        if roas >= 2.5:
            semaforo = "🟢"
        elif roas >= 1.5:
            semaforo = "🟡"
        else:
            semaforo = "🔴"

        ayer = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime("%d/%m/%Y")

        mensaje = (
            f"📊 <b>REPORTE META ADS — {ayer}</b>\n"
            f"{'═'*28}\n\n"
            f"💸 <b>Gasto:</b> ${gasto:.2f} USD\n"
            f"👁️ <b>Impresiones:</b> {impresiones:,}\n"
            f"🖱️ <b>Clicks:</b> {clicks:,}\n"
            f"📈 <b>CTR:</b> {ctr:.2f}%\n"
            f"💵 <b>CPC:</b> ${cpc:.2f} USD\n\n"
            f"🛒 <b>Compras:</b> {compras}\n"
            f"📦 <b>Costo/compra:</b> ${costo_compra:.2f} USD\n"
            f"{semaforo} <b>ROAS:</b> {roas:.2f}x\n\n"
        )

        if roas < 1.5 and gasto > 0:
            mensaje += "⚠️ <b>ALERTA:</b> ROAS bajo 1.5x — revisar anuncios activos.\n"
        elif roas >= 2.5:
            mensaje += "✅ ROAS saludable. Campaña funcionando bien.\n"

        send_telegram(mensaje)

    except Exception as e:
        send_telegram(f"⚠️ Error al obtener datos de Meta Ads:\n{str(e)}")

# ─── SCHEDULER ────────────────────────────────────────────────────
def job_diario():
    reporte_carros_abandonados()
    time.sleep(3)
    reporte_meta_ads()

def main():
    print("🤖 Bot Soulcute iniciado. Esperando las 7:00 AM (Santiago)...")
    send_telegram("✅ <b>Bot Soulcute activo.</b>\nReportes diarios programados a las 7:00 AM.")

    schedule.every().day.at("07:00").do(job_diario)

    while True:
        hora_actual = datetime.now(TIMEZONE)
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
