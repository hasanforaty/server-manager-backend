FROM python:3.9-alpine3.13
LABEL maintainer="https://hasanforaty.github.io/"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./server_manager_backend /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /env && \
    /env/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    apk add gcc  python3-dev libffi-dev openssl-dev cargo pkgconfig && \
    /env/bin/pip install cryptography && \
    /env/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = 'true' ] ; \
        then /env/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/env/bin:$PATH"
USER django-user


