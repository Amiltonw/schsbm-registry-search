FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV DJANGO_SETTINGS_MODULE nrn_search.settings

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt && pip install python-dotenv

COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh"]