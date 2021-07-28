FROM python:3.8.5
WORKDIR /code
COPY ./foodgram_backend .
RUN pip install -r requirements.txt
CMD gunicorn foodgram_backend.wsgi:application --bind 0.0.0.0:8000 