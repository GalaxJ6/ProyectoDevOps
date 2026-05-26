# Observabilidad

La API expone los siguientes recursos:

- `GET /health`: devuelve estado de salud de la aplicación y la base de datos.
- `GET /metrics`: métricas Prometheus para requests y latencia.

También se generan logs estructurados en JSON usando `python-json-logger`.

## Prometheus y Grafana

Se puede levantar el stack con `docker-compose up --build` y acceder a:

- API: `http://localhost:5000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Prometheus está configurado en `prometheus.yml` para scrapear `http://todo-api:5000/metrics`.
