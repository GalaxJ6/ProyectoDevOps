# 📟 Referencia Rápida de Comandos

Todos los comandos para ejecutar cada componente del proyecto To-Do API.

---

## 1️⃣ SETUP INICIAL

### Clonar repositorio
```bash
git clone <URL_REPOSITORIO>
cd devops-final-seed
```

### Instalar dependencias (desarrollo)
```bash
pip install -r requirements-dev.txt
```

### Instalar dependencias (producción)
```bash
pip install -r requirements.txt
```

### Instalar pre-commit hooks
```bash
pip install pre-commit
pre-commit install
```

---

## 2️⃣ DESARROLLO LOCAL

### Ejecutar API sin Docker
```bash
python src/app.py
```

**Output esperado**:
```
* Running on http://0.0.0.0:5000
```

**Acceder**:
- API: http://localhost:5000
- Health: http://localhost:5000/health
- Metrics: http://localhost:5000/metrics

---

## 3️⃣ TESTS

### Ejecutar todos los tests
```bash
pytest -q
```

### Ejecutar tests con verbosidad
```bash
pytest -v
```

### Ejecutar un test específico
```bash
pytest tests/test_app.py::test_create_task -v
```

### Ejecutar con cobertura de código
```bash
pytest --cov=src tests/
```

### Ver cobertura en HTML
```bash
pytest --cov=src --cov-report=html tests/
# Abrir htmlcov/index.html en navegador
```

### Ejecutar tests en paralelo
```bash
pytest -n auto tests/
```

---

## 4️⃣ LINTING & SEGURIDAD

### Linting con flake8
```bash
flake8 src tests
```

### Linting solo una carpeta
```bash
flake8 src/
```

### Auditoría de dependencias
```bash
pip_audit
```

### Security scanning con Bandit
```bash
bandit -r src/
```

### Pre-commit: ejecutar todos los checks
```bash
pre-commit run --all-files
```

### Pre-commit: ejecutar un hook específico
```bash
pre-commit run flake8 --all-files
```

### Formatear código con Black
```bash
black src/ tests/
```

### Organizar imports con isort
```bash
isort src/ tests/
```

---

## 5️⃣ DOCKER

### Construir imagen Docker
```bash
docker build -t todo-api:latest .
```

### Construir con tag específico
```bash
docker build -t todo-api:v1.0.0 .
```

### Listar imágenes
```bash
docker images | grep todo-api
```

### Ejecutar contenedor individual
```bash
docker run -p 5000:5000 -v $(pwd)/data:/data todo-api:latest
```

### Ejecutar contenedor con shell
```bash
docker run -it todo-api:latest /bin/bash
```

### Verificar usuario dentro del contenedor
```bash
docker run --rm todo-api:latest id
# Output: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
```

### Ver logs del contenedor
```bash
docker logs <CONTAINER_ID>
```

### Detener contenedor
```bash
docker stop <CONTAINER_ID>
```

---

## 6️⃣ DOCKER COMPOSE

### Levantar stack completo (build + up)
```bash
docker compose up --build
```

### Levantar stack sin rebuild
```bash
docker compose up
```

### Ejecutar en background
```bash
docker compose up -d --build
```

### Ver logs
```bash
docker compose logs -f
```

### Ver logs de servicio específico
```bash
docker compose logs -f todo-api
docker compose logs -f prometheus
docker compose logs -f grafana
```

### Detener servicios
```bash
docker compose down
```

### Detener y eliminar volúmenes
```bash
docker compose down -v
```

### Listar servicios corriendo
```bash
docker compose ps
```

### Ejecutar comando en contenedor
```bash
docker compose exec todo-api python -m pytest -q
```

---

## 7️⃣ ACCESO A SERVICIOS (Docker Compose)

### API
```bash
curl http://localhost:5000
curl http://localhost:5000/health
curl http://localhost:5000/metrics
```

### Crear tarea
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Mi tarea", "description": "Descripción"}'
```

### Listar tareas
```bash
curl http://localhost:5000/tasks
```

### Obtener tarea específica
```bash
curl http://localhost:5000/tasks/1
```

### Actualizar tarea
```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Nueva tarea", "completed": true}'
```

### Eliminar tarea
```bash
curl -X DELETE http://localhost:5000/tasks/1
```

### Prometheus
```
http://localhost:9090
```

Query ejemplo:
```promql
sum(rate(todo_api_requests_total[1m])) by (endpoint)
```

### Grafana
```
http://localhost:3000
Usuario: admin
Contraseña: admin
```

---

## 8️⃣ KUBERNETES

### Verificar que kubectl está instalado
```bash
kubectl version --client
```

### Aplicar todos los manifests
```bash
kubectl apply -f k8s/
```

### Aplicar manifest específico
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/persistentvolumeclaim.yaml
kubectl apply -f k8s/configmap.yaml
```

### Ver Deployments
```bash
kubectl get deployments
```

### Ver Pods
```bash
kubectl get pods
```

### Ver Pods con labels
```bash
kubectl get pods -l app=todo-api
```

### Ver Pods con más detalles
```bash
kubectl get pods -o wide
```

### Describir Pod
```bash
kubectl describe pod <POD_NAME>
```

### Ver logs de Pod
```bash
kubectl logs <POD_NAME>
```

### Ver logs en tiempo real
```bash
kubectl logs <POD_NAME> -f
```

### Ver logs de todos los pods con label
```bash
kubectl logs -l app=todo-api -f
```

### Ejecutar comando en Pod
```bash
kubectl exec -it <POD_NAME> -- /bin/bash
```

### Port-forward a local
```bash
kubectl port-forward svc/todo-api 5000:5000
```

### Ver Services
```bash
kubectl get svc
```

### Ver PersistentVolumeClaims
```bash
kubectl get pvc
```

### Ver ConfigMaps
```bash
kubectl get configmaps
```

### Ver Secrets
```bash
kubectl get secrets
```

### Describir ConfigMap
```bash
kubectl describe configmap todo-api-config
```

### Editar ConfigMap
```bash
kubectl edit configmap todo-api-config
```

### Actualizar deployment (con nueva imagen)
```bash
kubectl set image deployment/todo-api \
  todo-api=todo-api:v1.1.0
```

### Ver historial de cambios
```bash
kubectl rollout history deployment/todo-api
```

### Rollback a versión anterior
```bash
kubectl rollout undo deployment/todo-api
```

### Escalar deployment
```bash
kubectl scale deployment todo-api --replicas=3
```

### Ver eventos
```bash
kubectl get events
```

### Eliminar deployment
```bash
kubectl delete deployment todo-api
```

### Eliminar todo en namespace
```bash
kubectl delete -f k8s/
```

### Ver recursos de cluster
```bash
kubectl top nodes
kubectl top pods
```

### Crear namespace
```bash
kubectl create namespace todo-api-ns
```

### Cambiar namespace por defecto
```bash
kubectl config set-context --current --namespace=todo-api-ns
```

---

## 9️⃣ GIT & VERSIONING

### Ver estado
```bash
git status
```

### Agregar archivos
```bash
git add .
git add src/app.py
```

### Commit
```bash
git commit -m "Implementar mejoras DevOps"
```

### Push
```bash
git push origin main
```

### Ver logs de commits
```bash
git log --oneline -n 10
```

### Crear tag
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Ver tags
```bash
git tag
```

### Pre-commit antes de push
```bash
pre-commit run --all-files
```

---

## 🔟 CI/CD (GitHub Actions)

### Ver workflow en local
```bash
cat .github/workflows/ci-cd.yml
```

### Trigger workflow manualmente (en GitHub)
```
1. Ve a Actions
2. Selecciona workflow
3. Click "Run workflow"
```

### Ver artifacts
```
1. Ve a Actions
2. Click en workflow run
3. Descargar "reports"
```

### Descargar artefacto desde CLI
```bash
# Requiere GitHub CLI
gh run download <RUN_ID>
```

---

## 1️⃣1️⃣ PROMETHEUS & GRAFANA

### Verificar Prometheus está scrapeando
```
1. Abre http://localhost:9090
2. Status → Targets
3. Deberías ver "todo-api" con estado "Up"
```

### Query en Prometheus
```promql
# Requests total
todo_api_requests_total

# Tasa de requests por minuto
rate(todo_api_requests_total[1m])

# Latencia P50
histogram_quantile(0.5, rate(todo_api_request_latency_seconds_bucket[5m]))

# Latencia P95
histogram_quantile(0.95, rate(todo_api_request_latency_seconds_bucket[5m]))

# Tasa de errores
rate(todo_api_requests_total{http_status=~"5.."}[5m])
```

### Añadir Data Source en Grafana
```
1. Abre http://localhost:3000
2. Login: admin / admin
3. Home → Data sources → New data source
4. Prometheus → URL: http://prometheus:9090
5. Save
```

### Crear Dashboard
```
1. Home → + Create → Dashboard
2. Add panel → Prometheus
3. Ingresa query PromQL
4. Guarda panel
```

---

## 1️⃣2️⃣ MANTENIMIENTO

### Limpiar Docker
```bash
# Eliminar imágenes no usadas
docker image prune -a

# Eliminar contenedores parados
docker container prune

# Eliminar volúmenes no usados
docker volume prune

# Todo de una vez
docker system prune -a
```

### Actualizar dependencias
```bash
pip install --upgrade pip
pip install -U -r requirements-dev.txt
```

### Verificar vulnerabilidades
```bash
pip_audit
bandit -r src/
```

### Generar requirements.txt actualizado
```bash
pip freeze > requirements.txt
```

---

## 1️⃣3️⃣ TROUBLESHOOTING

### Ver qué procesos están escuchando puertos
```bash
# Linux/Mac
lsof -i :5000
lsof -i :9090
lsof -i :3000

# Windows
netstat -ano | findstr :5000
```

### Matar proceso en puerto
```bash
# Linux/Mac
kill -9 <PID>

# Windows
taskkill /PID <PID> /F
```

### Revisar logs de Docker Compose
```bash
docker compose logs --tail=100
docker compose logs -f todo-api
```

### Verificar salud de contenedor
```bash
docker compose ps
docker inspect <CONTAINER_ID>
```

### Conectar a base de datos SQLite
```bash
sqlite3 data/tasks.db
SELECT * FROM tasks;
```

### Revisar espacio de disco
```bash
docker system df
```

---

## 1️⃣4️⃣ EJEMPLOS DE FLUJO COMPLETO

### Desarrollo local
```bash
# 1. Instalar dependencias
pip install -r requirements-dev.txt

# 2. Ejecutar tests
pytest -q

# 3. Linting
flake8 src tests

# 4. Ejecutar API local
python src/app.py

# 5. En otra terminal, hacer requests
curl http://localhost:5000/health
```

### Con Docker Compose
```bash
# 1. Levantar stack
docker compose up --build

# 2. Esperar a que esté ready (~30s)

# 3. En otra terminal, hacer requests
curl http://localhost:5000/tasks
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Tarea 1"}'

# 4. Ver métricas en Prometheus
# http://localhost:9090

# 5. Ver dashboards en Grafana
# http://localhost:3000 (admin/admin)

# 6. Detener
docker compose down
```

### Con Kubernetes (local)
```bash
# 1. Asegurar cluster local (minikube, docker-desktop)
kubectl cluster-info

# 2. Aplicar manifests
kubectl apply -f k8s/

# 3. Esperar a que esté ready
kubectl get pods -l app=todo-api -w

# 4. Port-forward
kubectl port-forward svc/todo-api 5000:5000

# 5. En otra terminal
curl http://localhost:5000/health

# 6. Ver logs
kubectl logs -l app=todo-api -f

# 7. Limpiar
kubectl delete -f k8s/
```

### Pipeline CI/CD
```bash
# 1. Make changes
nano src/app.py

# 2. Test locally
pytest -q
flake8 src tests

# 3. Pre-commit hooks
pre-commit run --all-files

# 4. Commit y push
git add .
git commit -m "Feat: nueva funcionalidad"
git push origin main

# 5. GitHub Actions se ejecuta automáticamente
# Ver en: https://github.com/USER/REPO/actions

# 6. Descargar artefactos
# Actions → workflow → artifacts → reports
```

---

## 1️⃣5️⃣ CHEAT SHEET RÁPIDO

```bash
# Setup
pip install -r requirements-dev.txt

# Test
pytest -q

# Lint
flake8 src tests

# Security
pip_audit && bandit -r src/

# Docker build
docker build -t todo-api:latest .

# Docker Compose
docker compose up --build
docker compose logs -f
docker compose down

# Kubernetes
kubectl apply -f k8s/
kubectl get pods -l app=todo-api
kubectl logs -l app=todo-api -f
kubectl port-forward svc/todo-api 5000:5000

# API tests
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/metrics

# Prometheus
http://localhost:9090

# Grafana
http://localhost:3000 (admin/admin)
```

---

## 📋 Tabla Resumen de Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| API | 5000 | http://localhost:5000 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |
| Base de datos | - | data/tasks.db |

---

## 📚 Archivos Relacionados

- [SUMMARY.md](SUMMARY.md) — Resumen completo
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) — Guía de requisitos
- [CHANGELOG.md](CHANGELOG.md) — Detalle de cambios
- [k8s/README.md](k8s/README.md) — Guía Kubernetes
- [docs/grafana-export-guide.md](docs/grafana-export-guide.md) — Grafana

---

**Última actualización**: 2026-05-26  
**Versión**: 1.0.0
