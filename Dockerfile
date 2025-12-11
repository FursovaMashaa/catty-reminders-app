FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Chromium для Playwright
RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
