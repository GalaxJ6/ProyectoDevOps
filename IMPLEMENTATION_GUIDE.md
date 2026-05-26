# Guía de Implementación — Trabajo Final DevOps

Documento de referencia para cumplimiento de requisitos del Trabajo Final DevOps (To-Do API).

---

## 1. Tests Unitarios ✅ COMPLETADO

**Requisito**: Mínimo 5 tests unitarios en carpeta `tests/`

### Estado
- **Archivo**: [tests/test_app.py](tests/test_app.py)
- **Cantidad de tests**: 5+ tests implementados
- **Frameworks**: pytest 7.4.0

### Implementación realizada
```bash
# Tests cubiertos:
✓ test_index_returns_api_info       → GET / devuelve info de API
✓ test_create_and_get_task          → POST /tasks y GET /tasks/<id>
✓ test_update_task                  → PUT /tasks/<id>
✓ test_delete_task                  → DELETE /tasks/<id>
✓ test_health_endpoint              → GET /health
✓ test_metrics_endpoint             → GET /metrics
```

### Cómo verificar
```bash
# Ejecutar tests
python -m pytest -q

# Con reporte de cobertura (opcional)
python -m pytest --cov=src tests/
```

### Mejoras pendientes (opcional)
- [ ] Agregar `pytest-cov` a `requirements-dev.txt` para reporte de cobertura
- [ ] Aumentar cobertura a 80%+ de líneas

---

## 2. Containerización (Docker) ✅ COMPLETADO

**Requisito**: Dockerfile + docker-compose.yml

### Estado
- **Dockerfile**: [Dockerfile](Dockerfile)
  - Base: Python 3.11-slim
  - Puerto: 5000 (interno)
  - Volumen: `/data` (persistencia SQLite)
  
- **docker-compose.yml**: [docker-compose.yml](docker-compose.yml)
  - Servicios: `todo-api`, `prometheus`, `grafana`
  - Puertos: 5000 (API), 9090 (Prometheus), 3000 (Grafana)

### Cómo ejecutar
```bash
# Construir y levantar stack completo
docker compose up --build

# Verificar servicios
curl http://localhost:5000/health       # API
curl http://localhost:5000/metrics      # Métricas
curl http://localhost:9090              # Prometheus
# Grafana en http://localhost:3000
```

### Mejoras pendientes (seguridad)
- [ ] **Crear usuario no-root en Dockerfile** (recomendación de seguridad)
  ```dockerfile
  RUN useradd -m -u 1000 appuser
  USER appuser
  ```

---

## 3. Pipeline CI/CD ✅ COMPLETADO

**Requisito**: GitHub Actions workflow en `.github/workflows/ci-cd.yml`

### Estado
- **Archivo**: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- **Eventos**: push a `main` + PRs hacia `main`

### Pasos del pipeline
1. ✅ Setup Python 3.11
2. ✅ Instalar dependencias dev
3. ✅ Auditoría de dependencias (`pip-audit`)
4. ✅ Linting (`flake8`)
5. ✅ Tests unitarios (`pytest`)
6. ✅ Build imagen Docker
7. ✅ Guardar artefactos (reporte + imagen tar)

### Cómo verificar
```bash
# Hacer push a main → workflow se ejecuta automáticamente en GitHub
# Ver en: https://github.com/TU_REPO/actions
```

### Mejoras pendientes
- [ ] **Publicar imagen a registry** (DockerHub/GHCR)
  - Requiere agregar secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
  - Ejemplo snippet en [REPORT_CHANGES.md](REPORT_CHANGES.md#integración-en-github-actions--guía-rápida)

- [ ] **Versionado semántico**
  ```yaml
  # En workflow, reemplazar:
  tags: todo-api:${{ github.ref_name }}  # v1.0.0, v1.1.0, etc.
  ```

---

## 4. Observabilidad ✅ COMPLETADO

**Requisito**: Logs estructurados, `/health`, `/metrics`, Prometheus/Grafana

### 4.1 Logs Estructurados
- **Status**: ✅ Implementado
- **Framework**: `python-json-logger`
- **Formato**: JSON estructurado con campos: `timestamp`, `level`, `event`, `method`, `path`, `status`, `duration_ms`

Verificar:
```bash
curl http://localhost:5000/tasks
# Verás logs en formato JSON en consola/contenedor
```

### 4.2 Endpoints de Observabilidad
- **GET /health** ✅
  ```bash
  curl http://localhost:5000/health
  # Response: {"status": "ok", "db": "connected"}
  ```

- **GET /metrics** ✅
  ```bash
  curl http://localhost:5000/metrics
  # Response: Formato Prometheus (text/plain)
  ```

### 4.3 Métricas Prometheus
Métricas configuradas:

| Métrica | Tipo | Labels |
|---------|------|--------|
| `todo_api_requests_total` | Counter | method, endpoint, http_status |
| `todo_api_request_latency_seconds` | Histogram | method, endpoint |

### 4.4 Prometheus
- **Status**: ✅ Corriendo en http://localhost:9090
- **Scraping**: Cada 15 segundos a `http://todo-api:5000/metrics`
- **Config**: [prometheus.yml](prometheus.yml)

Verificar:
```
1. Abre http://localhost:9090
2. Graph → Busca "todo_api_requests_total"
3. Deberías ver métricas de tu API
```

### 4.5 Grafana
- **Status**: ✅ Corriendo en http://localhost:3000
- **Credenciales**: admin / admin
- **Data Source**: Prometheus agregado automáticamente

**Crear dashboard**:
```
1. Home → + New → Dashboard
2. Add panel → Prometheus
3. Ejemplos de queries:
   - Requests/sec: sum(rate(todo_api_requests_total[1m])) by (endpoint)
   - Latencia p50: histogram_quantile(0.5, rate(todo_api_request_latency_seconds_bucket[5m]))
   - Errores: sum(rate(todo_api_requests_total{http_status=~"5.."}[1m]))
```

### Mejoras pendientes
- [ ] Crear dashboard JSON exportable en `docs/grafana-dashboard.json`
- [ ] Agregar alertas en Prometheus (règles de alert)
- [ ] Configurar notificaciones (email, Slack)

---

## 5. Seguridad ✅ COMPLETADO

**Requisito**: Auditoría de dependencias + linting

### 5.1 Auditoría de Dependencias
- **Tool**: `pip-audit` 2.10.0
- **Ejecución**: En pipeline CI/CD automáticamente

Ejecutar localmente:
```bash
python -m pip_audit
```

Resultado esperado: Sin vulnerabilidades críticas en dependencias.

### 5.2 Linting
- **Tool**: `flake8` 6.1.0
- **Ejecución**: En pipeline CI/CD automáticamente

Ejecutar localmente:
```bash
flake8 src tests
```

Configuración: `.flake8` (si necesitas ajustar reglas)

### Mejoras pendientes
- [ ] Agregar pre-commit hooks (local lint antes de push)
  ```bash
  # Crear .pre-commit-config.yaml
  ```

- [ ] Habilitar dependabot en GitHub para actualizaciones automáticas

- [ ] SAST (Static Application Security Testing) con `bandit`
  ```bash
  pip install bandit
  bandit -r src/
  ```

---

## 6. Kubernetes (Bonus) 🟡 COMPLETADO CON MEJORAS

**Requisito**: Manifests en `k8s/` (bonus)

### Estado
- **Deployment**: [k8s/deployment.yaml](k8s/deployment.yaml)
  - 2 replicas
  - Image: `todo-api:latest`
  - Recursos: No definidos (agregar)

- **Service**: [k8s/service.yaml](k8s/service.yaml)
  - Type: ClusterIP
  - Puerto: 5000

### Cómo usar
```bash
# Asumir que tienes un cluster k8s (minikube, kind, etc.)
kubectl apply -f k8s/

# Verificar
kubectl get pods -l app=todo-api
kubectl get svc todo-api
```

### Mejoras implementables (próximos pasos)

#### 6.1 Health Probes 🔴 PENDIENTE
Agregar a `deployment.yaml`:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### 6.2 Persistencia 🔴 PENDIENTE
Reemplazar `emptyDir` por `PersistentVolumeClaim`:
```yaml
volumes:
  - name: task-storage
    persistentVolumeClaim:
      claimName: todo-api-pvc
```

#### 6.3 ConfigMap y Secrets
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-api-config
data:
  DB_PATH: /data/tasks.db
---
apiVersion: v1
kind: Secret
metadata:
  name: todo-api-secrets
type: Opaque
stringData:
  API_KEY: "tu-key-aqui"  # si necesita
```

#### 6.4 Resource Limits
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "128Mi"
    cpu: "200m"
```

#### 6.5 Helm Chart (muy bonus)
```bash
# Crear estructura Helm
helm create todo-api-chart

# Instalar
helm install todo-api ./todo-api-chart -f values.yaml
```

---

## 7. Documentación ✅ COMPLETADO

**Requisito**: `docs/` con pipeline, branching, observabilidad, CALMS

### Archivos generados
| Archivo | Contenido |
|---------|-----------|
| [docs/README.md](docs/README.md) | Índice de documentación |
| [docs/pipeline.md](docs/pipeline.md) | CI/CD workflow explicado |
| [docs/branching.md](docs/branching.md) | Estrategia de ramas (git flow) |
| [docs/observability.md](docs/observability.md) | Logs, métricas, trazas |
| [docs/calms.md](docs/calms.md) | Principios CALMS (Culture, Automation, Lean, Measurement, Sharing) |

### Verificar
```bash
ls -la docs/
# Deberías ver 5+ archivos .md
```

### Mejoras pendientes
- [ ] Agregar ejemplos de curl para cada endpoint en `docs/api.md`
- [ ] Documentar dashboard Grafana (JSON exportado)
- [ ] Guía de troubleshooting

---

## 8. Artefactos ✅ COMPLETADO

**Requisito**: Imagen versionada + reportes de build

### 8.1 Imagen Versionada
En pipeline CI/CD:
```yaml
docker build -t todo-api:${{ github.sha }} .
```

Resultado: `todo-api:abc1234def5678...` (immutable por commit hash)

### 8.2 Reportes de Build
Pipeline genera en `reports/`:
- `junit.xml` — Resultados de tests
- `todo-api-<sha>.tar` — Imagen Docker empaquetada

**Verificar en GitHub**:
1. Ve a Actions → workflow reciente
2. Haz click en "artifacts"
3. Descarga el tar si quieres inspeccionar la imagen

### Mejoras pendientes
- [ ] **Tags semánticos**: 
  ```yaml
  # En workflow, agregar:
  docker tag todo-api:${{ github.sha }} todo-api:v1.0.0
  ```

- [ ] **Publicar en registry**:
  ```yaml
  docker push myuser/todo-api:v1.0.0
  docker push myuser/todo-api:latest
  ```

- [ ] **SBoM (Software Bill of Materials)**:
  ```bash
  pip install cyclonedx-bom
  cyclonedx-bom -o sbom.json
  ```

---

## 📋 Checklist de Cumplimiento

```
✅ = Completado
🟡 = Parcialmente completado / Mejoras pendientes
🔴 = No implementado

✅ Tests unitarios (5+ tests)
✅ Dockerfile (imagen 3.11-slim)
✅ docker-compose.yml (3 servicios)
✅ Pipeline CI/CD (pytest, flake8, pip-audit, docker build)
✅ Observabilidad (logs JSON, /health, /metrics, Prometheus, Grafana)
✅ Seguridad (auditoría, linting)
✅ Kubernetes (deployment.yaml, service.yaml)
  🟡 → Agregar: health probes, persistencia, configmap
✅ Documentación (pipeline, branching, observabilidad, CALMS)
✅ Artefactos (imagen con SHA, reports en artifacts)
  🟡 → Mejorar: tags semánticos, publicar en registry
```

---

## 🚀 Quick Start — Ejecutar Todo

### 1. Clonar y configurar
```bash
git clone <repo>
cd devops-final-seed
```

### 2. Instalar dependencias
```bash
pip install -r requirements-dev.txt
```

### 3. Ejecutar tests
```bash
python -m pytest -q
```

### 4. Levantar stack
```bash
docker compose up --build
```

### 5. Acceder a servicios
- API: http://localhost:5000
- Health: http://localhost:5000/health
- Metrics: http://localhost:5000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### 6. Hacer push a GitHub
```bash
git add .
git commit -m "DevOps implementation complete"
git push origin main
# → Pipeline ejecuta automáticamente
```

---

## 📖 Referencias

- [Flask documentation](https://flask.palletsprojects.com/)
- [Prometheus client library](https://github.com/prometheus/client_python)
- [Grafana dashboards](https://grafana.com/grafana/dashboards/)
- [Kubernetes official docs](https://kubernetes.io/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Última actualización**: 2026-05-26  
**Estado general**: 85% completado, listo para entregar
