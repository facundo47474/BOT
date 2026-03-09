# -*- coding: utf-8 -*-
"""
Servidor web para controlar el bot. Funciona local (con PC) o en la nube (24/7, sin PC).
Instalable como PWA en móvil y escritorio.
"""
import os
import threading
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from bot import run_bot

app = Flask(__name__, static_folder="static")

# Estado compartido
estado = {
    "corriendo": False,
    "mensaje": "",
    "entrada_disponible": False,
    "checkout_url": "",
    "error": None,
}
stop_event = threading.Event()
THREAD_BOT = None

# En nube (Railway, Render) usamos headless. Local puede usar ventana visible.
EN_NUBE = bool(os.getenv("PORT") or os.getenv("BOCA_HEADLESS"))


def _on_entrada(checkout_url=""):
    estado["entrada_disponible"] = True
    estado["checkout_url"] = checkout_url or "https://bocasocios.bocajuniors.com.ar/"
    if EN_NUBE:
        estado["mensaje"] = "¡Entrada disponible! El bot reservó. Tocá 'Ir a comprar' para completar."
    else:
        estado["mensaje"] = "¡Entrada disponible! Completa la compra en la ventana del navegador."
    estado["corriendo"] = False


def _on_error(err):
    estado["error"] = err
    estado["mensaje"] = f"Error: {err}"
    estado["corriendo"] = False


def _on_status_update(msg):
    estado["mensaje"] = msg


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.static_folder, "manifest.json")


@app.route("/sw.js")
def sw():
    return send_from_directory(app.static_folder, "sw.js", mimetype="application/javascript")


@app.route("/api/estado")
def api_estado():
    return jsonify(estado)


@app.route("/api/iniciar", methods=["POST"])
def api_iniciar():
    global THREAD_BOT
    if estado["corriendo"]:
        return jsonify({"ok": False, "mensaje": "El bot ya está en ejecución."})
    estado["corriendo"] = True
    estado["mensaje"] = "Bot iniciado: login y recarga en curso..."
    estado["entrada_disponible"] = False
    estado["checkout_url"] = ""
    estado["error"] = None
    stop_event.clear()
    THREAD_BOT = threading.Thread(
        target=run_bot,
        kwargs={
            "headless": EN_NUBE,
            "on_entrada_disponible": _on_entrada,
            "on_status_update": _on_status_update,
            "on_error": _on_error,
            "stop_flag": stop_event,
        },
        daemon=True,
    )
    THREAD_BOT.start()
    return jsonify({"ok": True, "mensaje": "Bot iniciado."})


@app.route("/api/detener", methods=["POST"])
def api_detener():
    if not estado["corriendo"]:
        return jsonify({"ok": True, "mensaje": "El bot no estaba en ejecución."})
    stop_event.set()
    estado["corriendo"] = False
    estado["mensaje"] = "Detenido."
    return jsonify({"ok": True, "mensaje": "Bot detenido."})


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#0d47a1">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Boca Bot">
  <link rel="manifest" href="/manifest.json">
  <link rel="apple-touch-icon" href="/static/icon-192.png">
  <title>Bot Entradas Boca</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
      background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
      color: #fff;
      min-height: 100vh;
      margin: 0;
      padding: 1rem;
      padding-top: max(1rem, env(safe-area-inset-top));
      padding-bottom: max(1rem, env(safe-area-inset-bottom));
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .card {
      background: rgba(255,255,255,0.12);
      border-radius: 1rem;
      padding: 1.5rem;
      max-width: 420px;
      width: 100%;
      backdrop-filter: blur(8px);
    }
    h1 { margin: 0 0 0.5rem; font-size: 1.4rem; }
    .sub { opacity: 0.85; font-size: 0.9rem; margin-bottom: 1.2rem; }
    #estado {
      background: rgba(0,0,0,0.2);
      border-radius: 0.5rem;
      padding: 0.75rem;
      margin-bottom: 1rem;
      min-height: 2.5rem;
      font-size: 0.95rem;
    }
    .entrada-ok { background: #1b5e20 !important; color: #fff; font-weight: bold; }
    .btns { display: flex; gap: 0.75rem; flex-wrap: wrap; }
    button {
      flex: 1;
      min-width: 120px;
      padding: 0.85rem 1rem;
      border: none;
      border-radius: 0.5rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.1s, opacity 0.2s;
    }
    button:active { transform: scale(0.98); }
    button:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-iniciar { background: #4caf50; color: #fff; }
    .btn-detener { background: #f44336; color: #fff; }
    .btn-comprar {
      display: block !important;
      background: #ffd700;
      color: #000;
      text-align: center;
      text-decoration: none;
      padding: 1rem;
      border-radius: 0.5rem;
      font-weight: bold;
      margin-top: 1rem;
    }
    .aviso {
      margin-top: 1rem;
      font-size: 0.8rem;
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Bot Entradas Boca</h1>
    <p class="sub">Iniciá el bot desde acá, funciona 24/7 sin PC.</p>
    <div id="estado">Inactivo. Tocá &quot;Iniciar bot&quot; para empezar.</div>
    <div class="btns">
      <button class="btn-iniciar" id="btnIniciar" onclick="iniciar()">Iniciar bot</button>
      <button class="btn-detener" id="btnDetener" onclick="detener()" disabled>Detener</button>
    </div>
    <a id="btnComprar" href="#" target="_blank" rel="noopener" class="btn-comprar" style="display:none;">🎫 Ir a completar compra</a>
    <p class="aviso">Cuando haya entrada disponible, el bot reservará y te avisará. Completá la compra en Boca Socios.</p>
    <p class="instalar">📲 <strong>Instalar como app:</strong> Menú del navegador → &quot;Instalar&quot; o &quot;Agregar a pantalla de inicio&quot;</p>
  </div>
  <script>
    const estadoEl = document.getElementById('estado');
    const btnIniciar = document.getElementById('btnIniciar');
    const btnDetener = document.getElementById('btnDetener');

    const btnComprar = document.getElementById('btnComprar');
    function actualizarEstado() {
      fetch('/api/estado').then(r => r.json()).then(d => {
        estadoEl.textContent = d.mensaje || 'Inactivo';
        estadoEl.classList.toggle('entrada-ok', d.entrada_disponible);
        btnIniciar.disabled = d.corriendo;
        btnDetener.disabled = !d.corriendo;
        if (d.entrada_disponible) {
          btnComprar.href = d.checkout_url || 'https://bocasocios.bocajuniors.com.ar/';
          btnComprar.style.display = 'block';
          if (typeof Notification !== 'undefined' && Notification.permission === 'granted')
            new Notification('¡Entrada Boca disponible!', { body: 'Tocá para ir a completar la compra.' });
        } else {
          btnComprar.style.display = 'none';
        }
      }).catch(() => { estadoEl.textContent = 'Error al conectar'; });
    }

    function iniciar() {
      fetch('/api/iniciar', { method: 'POST' }).then(r => r.json()).then(d => {
        actualizarEstado();
      });
    }

    function detener() {
      fetch('/api/detener', { method: 'POST' }).then(r => r.json()).then(() => actualizarEstado());
    }

    actualizarEstado();
    setInterval(actualizarEstado, 2000);
    if (typeof Notification !== 'undefined') Notification.requestPermission();

    // Registrar Service Worker para PWA
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("Servidor Bot Boca: abre en el navegador http://127.0.0.1:" + str(port))
    print("Desde el celular (misma WiFi): usa la IP de esta PC, ej: http://192.168.1.10:" + str(port))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
