# Dockerfile para API de Procesamiento de Imágenes con Gemini

# Utilizar una imagen base oficial de Python 3.12
FROM python:3.12-slim

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    # SSL dependencies
    openssl \
    libssl-dev \
    ca-certificates \
    # Build dependencies
    build-essential \
    python3-dev \
    gcc \
    # Utils
    curl \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip, setuptools y wheel
RUN python -m pip install --upgrade pip setuptools wheel

# Instalar Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos de Poetry al directorio de trabajo
COPY pyproject.toml poetry.lock ./

# Instalar las dependencias del proyecto (sin crear virtualenv)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root 

# Copiar el código de la aplicación al directorio de trabajo
COPY app ./app

# Copiar el frontend
COPY frontend ./frontend

# Copiar README
COPY README.md ./README.md
# Cambiar propiedad del directorio /app al usuario no-root
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer el puerto de la aplicación
EXPOSE 8000

# Establecer la variable de entorno PORT
ENV PORT=8000

# NOTA: La API key de Gemini debe pasarse en runtime con:
# docker run -e GEMINI_API_KEY=tu_api_key_aqui ...
# NO incluir la API key aquí por seguridad

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
