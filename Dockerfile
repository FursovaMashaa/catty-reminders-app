FROM python:3.12-slim

WORKDIR /app

# Установка только необходимого минимума
RUN pip install --no-cache-dir fastapi uvicorn

COPY app/main.py .
COPY config.json .

EXPOSE 8181

# Простой запуск для демонстрации Lab 4
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181", "--reload"]
