# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

#
ENV PYTHONPATH=/app

# Expone el puerto en el que se ejecuta la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
