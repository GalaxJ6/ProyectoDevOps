# Reporte de cambios y guía de uso — To-Do API (DevOps Seed)

A continuación están los comandos principales para ejecutar tests, levantar contenedores y los pasos para integrar todo en GitHub Actions y Grafana.

## Comandos rápidos

- Instalar dependencias runtime:

```bash
pip install -r requirements.txt
```

- Instalar dependencias de desarrollo (tests, lint, auditoría):

```bash
pip install -r requirements-dev.txt
```

- Ejecutar tests unitarios:

```bash
python -m pytest -q
```

- Levantar el stack con Docker Compose (API, Prometheus, Grafana):

```bash
docker compose up --build
```

- Construir solo la imagen Docker de la aplicación:

```bash
docker build -t todo-api:latest .
```

## Qué añadí (archivos principales)

- **App / observabilidad**: [src/app.py](src/app.py)
- **Dependencias dev**: [requirements-dev.txt](requirements-dev.txt)
- **Tests**: [tests/test_app.py](tests/test_app.py)
- **Docker**: [Dockerfile](Dockerfile)
- **Docker Compose**: [docker-compose.yml](docker-compose.yml)
- **Prometheus config**: [prometheus.yml](prometheus.yml)
- **CI/CD**: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- **Docs**: [docs/README.md](docs/README.md), [docs/pipeline.md](docs/pipeline.md), [docs/observability.md](docs/observability.md)
- **Kubernetes (bonus)**: [k8s/deployment.yaml](k8s/deployment.yaml), [k8s/service.yaml](k8s/service.yaml)
- **Reporte**: [REPORT_CHANGES.md](REPORT_CHANGES.md)

Todos los cambios fueron aplicados al repositorio y la suite de pruebas pasa localmente (5 tests, todos OK en mi verificación).

## Resumen técnico de lo que implementé

- Endpoints nuevos para observabilidad:
  - `GET /health` — healthcheck básico que valida acceso a SQLite.
  - `GET /metrics` — métricas Prometheus (registro personalizado por instancia de app).
- Logs estructurados en JSON con `python-json-logger`.
- Métricas:
  - Contador `todo_api_requests_total{method,endpoint,http_status}`
  - Histograma `todo_api_request_latency_seconds{method,endpoint}`
- Tests automatizados con `pytest` cubriendo creación, lectura, actualización, borrado y endpoints de observabilidad.
- Pipeline de GitHub Actions que instala dependencias, ejecuta `pip-audit`, `flake8`, `pytest`, construye la imagen Docker y publica artefactos (tar de la imagen) como reporte.
- `docker-compose.yml` incluye servicios: `todo-api`, `prometheus` y `grafana` y volumen para persistir `tasks.db`.

## Integración en GitHub Actions — guía rápida

1. Subir el repositorio (push) con la estructura actual; el workflow existe en `.github/workflows/ci-cd.yml` y se activa en pushes y PRs hacia `main`.
2. Ajustes opcionales para publicar imagen en un registry:
   - Añadir secretos en GitHub: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` (o `GHCR_PAT`).
   - Reemplazar pasos de `docker build` en el workflow por `docker/build-push-action` para hacer `push` con tags (ejemplo: `docker/build-push-action@v4`).
3. Artefactos: el job ya genera `reports/` y sube con `actions/upload-artifact`.
4. Recomendación: configurar `paths-ignore` si no quieres ejecutar CI en cambios de docs o archivos grandes.

Ejemplo mínimo para publicar imagen (snippet para `.github/workflows/ci-cd.yml`):

```yaml
- name: Login to DockerHub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v4
  with:
    push: true
    tags: myuser/todo-api:${{ github.sha }}
```

## Observabilidad / Grafana — guía práctica

1. Levanta el stack con `docker compose up --build`.
2. Verifica Prometheus en `http://localhost:9090` y Grafana en `http://localhost:3000`.
3. En Grafana:
   - Añade una data source de tipo **Prometheus** apuntando a `http://prometheus:9090` si Grafana corre en compose; si accedes localmente desde el host, usa `http://localhost:9090`.
   - Crear dashboard con paneles sugeridos:
     - Requests por segundo: consulta `sum(rate(todo_api_requests_total[1m])) by (endpoint)`
     - Latencia (p50/p95): `histogram_quantile(0.5, sum(rate(todo_api_request_latency_seconds_bucket[5m])) by (le, endpoint))` y `histogram_quantile(0.95, ...)`
     - Errores por endpoint: `sum(rate(todo_api_requests_total{http_status=~"5.."}[5m])) by (endpoint)`
   - Opcional: importar JSON de dashboard si quieres guardar una plantilla.
4. Alerts (opcional): definir reglas en Prometheus/Grafana para:
   - Healthcheck fallando: si `up{job="todo-api"}` desaparece o `probe` falla.
   - Alto error rate o latencias altas.

## Seguridad y calidad

- Auditoría de dependencias: el workflow ejecuta `pip-audit`. Localmente puedes ejecutar `python -m pip_audit`.
- Linting: `flake8 src tests` (ya en pipeline). Ajusta reglas en `.flake8` si lo deseas.

## Buenas prácticas y pasos recomendados antes de entregar

- Configura secrets en GitHub si vas a publicar la imagen en DockerHub o GHCR.
- Ajusta el workflow para versiones: usar tags semánticos (`v1.0.0`) y en el job usar `tags: myuser/todo-api:${{ github.ref_name }}` o `:${{ github.sha }}` para inmutabilidad.
- Añadir `health` probe en manifests de Kubernetes: `readinessProbe`/`livenessProbe` apuntando a `/health`.
- Persistencia en Kubernetes: reemplazar `emptyDir` por `PersistentVolumeClaim` para la `db`.
- Habilitar backups de `tasks.db` si quieres persistencia durable fuera del contenedor.

## Cómo comprobar que todo funciona (paso a paso)

1. Instala dependencias:

```bash
pip install -r requirements-dev.txt
```

2. Ejecuta tests:

```bash
python -m pytest -q
```

3. Levanta el stack:

```bash
docker compose up --build
```

4. Abre y revisa:
   - API: `http://localhost:5000`
   - Health: `http://localhost:5000/health`
   - Metrics: `http://localhost:5000/metrics`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000`

## Notas finales y próximos pasos sugeridos

- Si quieres, puedo:
  - Añadir `README` más detallado con ejemplos curl para cada endpoint.
  - Crear dashboards de Grafana exportables (JSON) y añadirlos a `docs/`.
  - Extender el pipeline para desplegar automáticamente en un cluster (eks/gke/aks) usando `kubectl` y `kubeconfig` como secret.

---

Generado automáticamente: cambios aplicados en el repositorio. Si deseas, hago el commit y creo un tag semántico ahora.
