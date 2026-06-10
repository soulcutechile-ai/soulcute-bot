# 🤖 Bot Soulcute Reportes

Bot de Telegram que envía cada día a las 7:00 AM (hora Chile):
- 🛒 Reporte de carros abandonados (Shopify)
- 📊 Reporte de rendimiento Meta Ads

---

## 📁 Archivos
- `main.py` — el bot
- `requirements.txt` — librerías necesarias
- `railway.toml` — configuración de Railway

---

## 🚀 Cómo subir a Railway (paso a paso)

### 1. Crear cuenta en GitHub
- Ve a github.com y crea una cuenta gratis
- Crea un repositorio nuevo llamado `soulcute-bot` (público o privado)
- Sube estos 3 archivos al repositorio

### 2. Crear cuenta en Railway
- Ve a railway.app
- Regístrate con tu cuenta de GitHub
- Clic en "New Project" → "Deploy from GitHub repo"
- Selecciona `soulcute-bot`

### 3. Configurar variables de entorno en Railway
En Railway, ve a tu proyecto → Variables → agrega estas:

| Variable | Valor |
|---|---|
| TELEGRAM_TOKEN | 8709802667:AAFZBJcTzbNlG0i5FUSq8YgQ5IyL7tI1v08 |
| TELEGRAM_CHAT_ID | 7686383531 |
| SHOPIFY_STORE | soulcute.myshopify.com |
| SHOPIFY_TOKEN | (tu Admin API token de Shopify) |
| META_ACCESS_TOKEN | (tu token de Meta Ads) |
| META_AD_ACCOUNT | act_1112157504418218 |

### 4. Deploy
- Railway desplegará automáticamente
- Verás en Telegram: "✅ Bot Soulcute activo"
- Desde ese momento, cada día a las 7:00 AM recibirás los reportes

---

## 🔑 Cómo obtener el Shopify Admin API Token
1. En Shopify Admin → Configuración → Aplicaciones y canales
2. Desarrollar aplicaciones → Crear una aplicación
3. Nombre: "Bot Reportes"
4. Permisos necesarios: `read_orders`, `read_checkouts`, `read_customers`
5. Instalar app → copia el "Admin API access token"

## 🔑 Cómo obtener el Meta Access Token
1. Ve a business.facebook.com → Configuración del negocio
2. Usuarios → Usuarios del sistema → Agregar usuario del sistema
3. Asigna rol "Analista" a tu cuenta de anuncios
4. Generar token → selecciona permisos: `ads_read`, `ads_management`
5. Copia el token generado
