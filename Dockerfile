FROM python:3.12-slim  # slim версия легче и быстрее

WORKDIR /app

# Копируем только requirements сначала (для кэширования)
COPY requirements.txt .

# Устанавливаем зависимости с флагами для ускорения
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 \
    fastapi uvicorn jinja2  # основные пакеты ставим сразу

# Копируем остальное
COPY . .

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
