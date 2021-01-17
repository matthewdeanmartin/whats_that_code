FROM python:3.9.0-slim-buster
WORKDIR /app
ENV PIP_NO_CACHE_DIR=off
ENV PYTHONUNBUFFERED=1
# RUN apk add --no-cache linux-headers==4.19.36-r0 wget
RUN python -m pip install --no-cache-dir --upgrade pip --quiet \
    && pip install pipenv  --no-cache-dir --quiet
COPY dist/* /app/
RUN pipenv install so_pip-*.whl --skip-lock
ENTRYPOINT ["pipenv", "run", "so_pip"]
