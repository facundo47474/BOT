# Usamos la imagen oficial de Playwright que ya incluye Python y los navegadores
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando de inicio
CMD ["python", "app.py"]