FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install playwright && \
    python -m playwright install --with-deps chromium

# Копируем ВСЁ приложение
COPY . .

# Убеждаемся, что есть init.py файлы
RUN touch app/__init__.py && \
    touch app/routers/__init__.py && \
    touch app/utils/__init__.py

EXPOSE 8181

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
