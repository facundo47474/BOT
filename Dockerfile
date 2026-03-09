# Bot Entradas Boca - Imagen para deploy en la nube
# Usa imagen oficial de Playwright (incluye Chromium y dependencias)
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000
ENV BOCA_HEADLESS=1

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 2 --timeout 300 app:app"]
