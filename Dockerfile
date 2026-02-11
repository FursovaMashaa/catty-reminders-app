FROM python:3.12-slim

WORKDIR /app

# Сначала копируем только requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальное приложение
COPY . .

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
