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

Seguí estos pasos para desplegar en Render:

1.  **Subir a GitHub:** Asegurate de que todos los archivos del proyecto (`Dockerfile`, `render.yaml`, etc.) estén en tu repositorio de GitHub.
2.  **Crear Servicio en Render:**
    *   En tu panel de Render, hacé clic en el botón **"New +"** y seleccioná **"Web Service"**.
    *   Conectá tu cuenta de GitHub y seleccioná el repositorio del bot.
3.  **Configuración Inicial:**
    *   Dale un nombre a tu servicio (ej: `boca-bot`).
    *   Render debería detectar que es un `Dockerfile`, así que la configuración del "Environment" y "Build Command" debería ser automática.
    *   Hacé clic en **"Create Web Service"**. El primer despliegue probablemente falle porque faltan las credenciales, ¡no te preocupes!
4.  **Agregar Credenciales (Paso Clave):**
    *   Una vez creado el servicio, andá a la pestaña **"Environment"**.
    *   Hacé clic en **"Add Environment Variable"** y agregá la primera variable:
        *   **Key:** `BOCA_EMAIL`
        *   **Value:** `tu-email-de-socio`
    *   Hacé clic de nuevo en **"Add Environment Variable"** para la segunda:
        *   **Key:** `BOCA_PASSWORD`
        *   **Value:** `tu-contraseña`
5.  **Desplegar de Nuevo:**
    *   Después de guardar las variables, andá a la pestaña **"Deploys"** y hacé clic en **"Deploy latest commit"** para volver a lanzar el despliegue, esta vez con las credenciales correctas.
    *   Una vez que termine, la URL pública de tu bot aparecerá en la parte superior del dashboard.

## Opción 2: Local (usando tu PC)

Si preferís correrlo en tu casa sin usar la nube:

1.  **Instalar dependencias**
   ```bash
   # Navegá a la carpeta donde descargaste el proyecto
   python -m venv venv                # Crea un entorno virtual
   venv\Scripts\activate              # Activa el entorno (en Windows)
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
