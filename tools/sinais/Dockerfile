# App de aprovação dos sinais (aprovacao.libras.se). Contexto de build: tools/sinais.
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg webp curl tzdata \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
ENV SINAIS_WORK=/dados/processamento \
    SINAIS_RAW=/dados/brutos \
    SINAIS_APROVACOES=/dados/aprovacoes.json \
    SINAIS_HOST=0.0.0.0 \
    SINAIS_ILUSTRACAO=fila \
    PORT=8790 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo
EXPOSE 8790
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD curl -fsS http://127.0.0.1:8790/saude || exit 1
CMD ["python3", "/app/aprovar.py", "--sem-navegador"]
