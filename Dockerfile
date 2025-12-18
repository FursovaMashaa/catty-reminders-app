FROM python:3.12-alpine  # ← Alpine вместо slim (в 5 раз меньше!)

# Устанавливаем только нужное для mysqlclient
RUN apk add --no-cache \
    mariadb-connector-c-dev \
    gcc \
    musl-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Используем Python wheel для ускорения
RUN pip install --no-cache-dir --upgrade pip wheel

# Сначала requirements для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом только нужные файлы
COPY app/ ./app/
COPY config.json ./

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
