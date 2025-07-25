FROM python:3.12-slim

ENV POETRY_VERSION=2.1.3
ENV PYTHONUNBUFFERED=1


RUN apt-get update \
 && apt-get install --no-install-recommends -y curl \
 && pip install --upgrade pip \
 && pip install "poetry==$POETRY_VERSION"

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
