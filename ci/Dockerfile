FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /service

COPY requirements.txt .
COPY pyproject.toml .

RUN uv sync --prerelease=allow

ENV PYTHONPATH=.:$PYTHONPATH

COPY . /service

RUN uv run ./download_model.py

ENTRYPOINT ["uv", "run"]
CMD ["python", "start.py"]