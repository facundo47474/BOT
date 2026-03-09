# Usamos la imagen oficial de Playwright que ya incluye Python y los navegadores
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]