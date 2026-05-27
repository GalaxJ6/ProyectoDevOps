# Observabilidad

## Componentes
- Logs estructurados JSON con `python-json-logger`.
- Endpoint de health: `GET /health`.
- Endpoint Prometheus: `GET /metrics`.
- Stack de monitoreo: Prometheus y Grafana.

## Requisitos para correr
- Docker y Docker Compose.
- Puertos libres: `5000`, `9090`, `3000`.
- Archivo `docker-compose.yml` presente.
- Archivo `prometheus.yml` configurado.

## Cómo ejecutar
```bash
docker compose up --build
```

## Verificación
- API: `http://localhost:5000`
- Health: `http://localhost:5000/health`
- Metrics: `http://localhost:5000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Prometheus
- URL de datasource en Grafana: `http://prometheus:9090`.
- Métricas principales:
  - `todo_api_requests_total`
  - `todo_api_request_latency_seconds`

## Logs
- Comando para seguir logs del servicio:
```bash
docker compose logs -f todo-api
```

- Los logs contienen campos JSON como `event`, `method`, `path`, `status`, `duration_ms`.
