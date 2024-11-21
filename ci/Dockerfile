FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /service

COPY pyproject.toml .

RUN uv sync --prerelease=allow

ENV PYTHONPATH=.:$PYTHONPATH

COPY . /service

ENTRYPOINT ["uv", "run"]
CMD ["python", "start.py"]