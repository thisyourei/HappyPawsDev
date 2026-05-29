FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY manage.py ./manage.py
COPY happypaws ./happypaws
COPY clinic ./clinic

RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "happypaws.wsgi:application", "--bind", ":8080", "--workers", "2"]
