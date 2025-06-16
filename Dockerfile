FROM python:3.10-slim

# Установка рабочей директории
WORKDIR /app

# Предотвращение создания .pyc файлов и обеспечение того, что вывод отображается в режиме реального времени
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка зависимостей
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование проекта
COPY . .

# Коллекция статических файлов
RUN python myAfisha/manage.py collectstatic --noinput

# Запуск приложения
CMD ["gunicorn", "--chdir", "myAfisha", "--bind", "0.0.0.0:8000", "myAfisha.wsgi:application"] 