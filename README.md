# Bot Entradas Boca Juniors

Bot que inicia sesión en **Boca Socios**, recarga la página en bucle hasta que haya entradas disponibles, reserva lugar y te avisa para que completes la compra vos mismo.

**Independiente y 24/7:** Desplegalo en la nube y usalo desde tu celular o PC en cualquier momento, sin tener tu computadora prendida.

**Instalable como app** (PWA) en iPhone, Android y PC.

---

## Opción 1: En la nube (recomendado, sin PC)

Desplegá el bot en Railway o Render. Funciona 24/7 y podés controlarlo desde cualquier dispositivo.

### Railway

1. Creá una cuenta en [railway.app](https://railway.app).
2. Clic en **"New Project"** → **"Deploy from GitHub repo"** (conectá tu repo) o **"Deploy from Dockerfile"**.
3. Si usás GitHub: subí este proyecto y elegilo. Railway detecta el `Dockerfile` automáticamente.
4. En **Variables** agregá:
   - `BOCA_EMAIL` = tu email de Boca Socios
   - `BOCA_PASSWORD` = tu contraseña
5. Deploy. Railway te da una URL tipo `https://tu-proyecto.up.railway.app`.
6. Abrí esa URL desde tu celular o PC e instalá la app (PWA).

### Render

1. Creá una cuenta en [render.com](https://render.com).
2. **New** → **Web Service**.
3. Conectá tu repo de GitHub o usá la opción de subir código.
4. En **Environment** → **Environment Variables** agregá:
   - `BOCA_EMAIL` = tu email
   - `BOCA_PASSWORD` = tu contraseña
5. Deploy. Te dan una URL tipo `https://boca-bot.onrender.com`.
6. Abrí esa URL e instalá la app.

### Uso en nube

1. Entrá a la URL de tu deploy (desde celular o PC).
2. Tocá **"Iniciar bot"**. El bot corre en el servidor.
3. Cuando haya entradas, verás **"Ir a completar compra"**. Tocá para ir a Boca Socios y terminar la compra.
4. Podés instalar como app (PWA) para tenerla en la pantalla de inicio.

---

## Opción 2: Local (con tu PC)

Si preferís correrlo en tu casa sin usar la nube:

1. **Instalar dependencias**
   ```bash
   cd "c:\Users\Usuario\Documents\libros\Testing QA\BOT"
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Credenciales** en `.env` (ya configurado).

3. **Iniciar**
   ```bash
   python app.py
   ```

4. Abrí http://127.0.0.1:5000 (o desde el celular en la misma WiFi: `http://TU_IP:5000`).

---

## Instalar como app (PWA)

| Dispositivo | Cómo instalar |
|-------------|---------------|
| **iPhone / iPad** | Safari → Compartir (□↑) → "Agregar a pantalla de inicio" |
| **Android** | Chrome → menú (⋮) → "Instalar aplicación" |
| **PC** | Chrome/Edge → icono "Instalar" en la barra de direcciones |

---

## Notas

- El bot **no** completa el pago: reserva lugar y te avisa para que vos termines.
- En nube, la reserva se hace en tu cuenta de Boca Socios; al abrir Boca Socios en tu celular (logueado) deberías ver la reserva para confirmar.
- Si Boca Socios cambia la web, revisá los selectores en `bot.py`.
