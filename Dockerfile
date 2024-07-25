FROM python:3.9-slim

WORKDIR /app

# Установим зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в рабочую директорию контейнера
COPY . .

# Команда для запуска приложения
CMD ["python", "app/main.py"]
