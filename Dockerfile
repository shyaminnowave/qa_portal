FROM python:3.10-alpine

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false --local
RUN poetry install
RUN poetry add psycopg2-binary
COPY . /app/
EXPOSE 8000

CMD poetry manage.py makemigrations && poetry manage.py migrate && poetry manage.py runserver 0.0.0.0:8000