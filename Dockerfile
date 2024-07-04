FROM python:3.11

WORKDIR /code

ENV POETRY_VIRTUALENVS_CREATE=0

RUN pip3 install poetry==1.8.2

ADD poetry.lock .
ADD pyproject.toml .
RUN poetry install --no-root

COPY ./src/ /code/
COPY .env /code/
