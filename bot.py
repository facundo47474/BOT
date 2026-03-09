# -*- coding: utf-8 -*-
"""
Bot para monitorear Boca Socios y reservar entrada cuando esté disponible.
Uso: se ejecuta desde app.py (servidor web) o directamente para pruebas.
"""
import os
import re
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv()

URL_SOCIOS = "https://bocasocios.bocajuniors.com.ar/"
URL_MAIN = "https://www.bocajuniors.com.ar/"

# Selectores (pueden cambiar si la web actualiza). Ajustar si el bot no encuentra los elementos.
SELECTOR_EMAIL = 'input[type="email"], input[name="email"], input[placeholder*="mail" i], input[id*="email" i]'
SELECTOR_PASSWORD = 'input[type="password"], input[name="password"], input[placeholder*="contraseña" i]'
SELECTOR_BTN_LOGIN = 'button[type="submit"], button:has-text("Ingresar"), button:has-text("Entrar"), a:has-text("Ingresar")'

# --- NUEVOS SELECTORES PARA EL FLUJO DE COMPRA ---
SELECTOR_VER_MAS = 'a:has-text("Ver más")'
SELECTOR_OBTENER_PLATEAS = 'a:has-text("Obtener Platea")'
# Suposición: los lugares disponibles son SVG verdes o tienen una clase "disponible". Ajustar si es necesario.
SELECTOR_LUGAR_DISPONIBLE = '[class*="disponible"], [class*="available"], [fill*="green"]'

# Intervalo entre recargas (segundos). No bajar mucho para no saturar el sitio.
INTERVALO_RECARGA = 3


def get_config():
    """Carga email, password y cantidad de entradas desde el entorno."""
    email = os.getenv("BOCA_EMAIL", "").strip()
    password = os.getenv("BOCA_PASSWORD", "").strip()
    # Por defecto, busca 1 entrada si no se especifica.
    cantidad_entradas = int(os.getenv("BOCA_CANTIDAD_ENTRADAS", "1"))

    if not email or not password:
        raise ValueError("Faltan BOCA_EMAIL o BOCA_PASSWORD en el archivo .env")
    return email, password, cantidad_entradas


def login(page, email, password):
    """Intenta hacer login en Boca Socios."""
    page.goto(URL_SOCIOS, wait_until="networkidle", timeout=30000)

    try:
        inp_email = page.locator(SELECTOR_EMAIL).first
        inp_email.wait_for(state="visible", timeout=10000)
        inp_email.fill(email)
    except PlaywrightTimeout:
        # Quizá ya está logueado o el formulario tiene otro selector
        if "bocasocios" in page.url and "login" not in page.url.lower():
            return True
        raise RuntimeError("No se encontró el campo de email. Revisa SELECTOR_EMAIL en bot.py.")

    try:
        inp_pass = page.locator(SELECTOR_PASSWORD).first
        inp_pass.wait_for(state="visible", timeout=5000)
        inp_pass.fill(password)
    except PlaywrightTimeout:
        raise RuntimeError("No se encontró el campo de contraseña. Revisa SELECTOR_PASSWORD en bot.py.")

    try:
        btn = page.locator(SELECTOR_BTN_LOGIN).first
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
    except PlaywrightTimeout:
        # Fallback si el botón no es clickeable pero el formulario puede enviarse con Enter
        page.keyboard.press("Enter")

    # Esperar a que la URL cambie o que aparezca un elemento post-login
    try:
        page.wait_for_url(lambda url: "login" not in url.lower(), timeout=15000)
    except PlaywrightTimeout:
        # Si la URL no cambia, puede que el login haya fallado.
        raise RuntimeError("El login no redirigió. Revisa las credenciales o la web de Boca Socios.")
    return True


def run_bot(headless=None, on_entrada_disponible=None, on_status_update=None, on_error=None, stop_flag=None):
    """
    Ejecuta el flujo: login, recarga en bucle, al detectar entrada reserva y notifica.
    headless: True en nube (sin ventana). Si None, usa env BOCA_HEADLESS.
    on_entrada_disponible(url): callback cuando reservó, recibe URL de checkout.
    on_error(err): callback con mensaje de error.
    on_status_update(msg): callback para reportar progreso.
    stop_flag: objeto con .is_set() para parar el bucle (ej. threading.Event).
    """
    try:
        email, password, cantidad_entradas = get_config()
        if headless is None:
            headless = os.getenv("BOCA_HEADLESS", "").lower() in ("1", "true", "yes")
        if stop_flag is None:
            class Dummy:
                def is_set(self): return False
            stop_flag = Dummy()
    except Exception as e:
        if on_error:
            on_error(f"Error de configuración: {e}")
        return

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"] if headless else []
            )
            context = browser.new_context(locale="es-AR")
            page = context.new_page()

            try:
                if on_status_update:
                    on_status_update("Iniciando sesión en Boca Socios...")
                login(page, email, password)
                if on_status_update:
                    on_status_update("Login exitoso. Buscando entradas...")
            except Exception as e:
                if on_error:
                    on_error(str(e))
                browser.close()
                return

            recargas = 0
            while not stop_flag.is_set():
                recargas += 1
                try:
                    page.reload(wait_until="networkidle", timeout=20000)
                except Exception:
                    try:
                        page.goto(URL_SOCIOS, wait_until="networkidle", timeout=20000)
                    except Exception as e:
                        if on_error:
                            on_error(f"Error al recargar: {e}")
                        if on_status_update:
                            on_status_update("Error al recargar, reintentando...")
                        time.sleep(INTERVALO_RECARGA)
                        continue

                # --- INICIO NUEVA LÓGICA DE BÚSQUEDA ---
                try:
                    # Paso 1: Buscar y hacer clic en "Ver más". Falla si no hay entradas.
                    page.locator(SELECTOR_VER_MAS).first.click(timeout=5000)

                    # Paso 2: Buscar y hacer clic en "Obtener Platea"
                    if on_status_update:
                        on_status_update("Navegando a plateas...")
                    page.locator(SELECTOR_OBTENER_PLATEAS).first.click(timeout=5000)

                    # Paso 3: En el mapa, buscar y seleccionar la cantidad de lugares disponibles
                    if on_status_update:
                        on_status_update("Buscando lugar disponible en el mapa...")
                    
                    lugares_disponibles = page.locator(SELECTOR_LUGAR_DISPONIBLE)
                    
                    # Esperamos a que al menos un lugar esté visible
                    lugares_disponibles.first.wait_for(state="visible", timeout=10000)

                    # ANTES DE HACER CLIC, VERIFICAMOS SI HAY SUFICIENTES ASIENTOS
                    if lugares_disponibles.count() >= cantidad_entradas:
                        if on_status_update:
                            on_status_update(f"¡Lugar disponible encontrado! Seleccionando {cantidad_entradas} entrada(s)...")

                        # Hacemos clic en los lugares la cantidad de veces necesaria
                        for i in range(cantidad_entradas):
                            lugares_disponibles.nth(i).click()
                            time.sleep(0.5) # Pequeña pausa entre clics

                        # Si llegamos acá, es un éxito. Notificamos y salimos.
                        page.wait_for_load_state("networkidle", timeout=15000)
                        if on_entrada_disponible:
                            on_entrada_disponible(page.url)
                        break # Salimos del bucle principal
                    # Si no hay suficientes asientos, no hacemos nada y el bucle de recarga continuará.

                except PlaywrightTimeout:
                    # Si algún paso falla (porque no hay entradas), simplemente continuamos con el siguiente ciclo.
                    pass

                if recargas % 5 == 0 and on_status_update:
                    on_status_update(f"Buscando entradas... (Ciclo #{recargas})")

                time.sleep(INTERVALO_RECARGA)

            # En modo local con ventana: mantener abierto para que el usuario complete
            if not headless:
                try:
                    while not stop_flag.is_set():
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            browser.close()
    except Exception as e:
        if on_error:
            on_error(f"Error crítico al iniciar navegador: {e}")


if __name__ == "__main__":
    run_bot(headless=False)
