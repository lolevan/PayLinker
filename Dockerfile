FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Устанавливаем PYTHONPATH для корректного импорта модулей
ENV PYTHONPATH=/app

# Добавляем команду ожидания перед выполнением миграций и запуском приложения
CMD ["sh", "-c", "sleep 10; python app/migrations/001_initial.py && python main.py"]