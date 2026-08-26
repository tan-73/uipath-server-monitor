FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVICE_PORT=8080 \
    STATE_FILE=/state/status

RUN addgroup -S -g 10001 demo \
    && adduser -S -D -H -u 10001 -G demo demo \
    && mkdir -p /app /state \
    && chown -R demo:demo /app /state

COPY --chown=demo:demo app/ /app/

USER 10001:10001
WORKDIR /app
VOLUME ["/state"]
EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=3s --retries=2 \
    CMD ["python", "/app/healthcheck.py"]

CMD ["python", "/app/server.py"]

