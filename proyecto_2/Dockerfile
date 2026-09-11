#Construri la imagen del servicio

#La imagen base

FROM python:3.12-slim

#la carpeta donde va a vivir todo dentro del contenerdor

WORKDIR /servicio

#Que los mensajes salgan inmediatamente 

ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1
    #Copíar solo el requirements 

RUN apt-get update && apt-get install -y --no-install-recommends \ libgomp1 \ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#Copíamos todos los archivos
COPY . .

#Documentacion del puerto
EXPOSE 8080

#Correr el desplieqgue del servicio
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]


