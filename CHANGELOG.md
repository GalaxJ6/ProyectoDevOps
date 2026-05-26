# Changelog — Mejoras DevOps Implementadas

Documento que detalla todas las mejoras implementadas al proyecto To-Do API.

## Fecha: 2026-05-26

### ✅ Cambios implementados

#### 1. Seguridad — Dockerfile
- **Cambio**: Agregar usuario no-root `appuser` (UID 1000)
- **Beneficio**: Reduce vector de ataque, cumple buenas prácticas de seguridad
- **Archivo**: [Dockerfile](../Dockerfile)

#### 2. Kubernetes — Deployment mejorado
**Archivo**: [k8s/deployment.yaml](../k8s/deployment.yaml)

**Health Probes agregadas**:
- `livenessProbe`: Reinicia pods muertos (15s delay, cada 10s)
- `readinessProbe`: Remueve del balancer si no está listo (5s delay, cada 5s)
- Ambas apuntan al endpoint `/health`

**Resource Limits**:
- **Requests**: 64Mi memoria, 100m CPU (garantizado)
- **Limits**: 256Mi memoria, 500m CPU (máximo)

**Persistencia**:
- Reemplazado `emptyDir` por `PersistentVolumeClaim`
- Ahora usa `todo-api-pvc` para persistencia de datos

**Otros**:
- Labels de versionado
- imagePullPolicy explícito

#### 3. Kubernetes — PersistentVolumeClaim
**Archivo**: [k8s/persistentvolumeclaim.yaml](../k8s/persistentvolumeclaim.yaml)

- Tamaño: 1Gi
- Modo: ReadWriteOnce
- Storage class: `standard` (ajustable)

#### 4. Kubernetes — ConfigMap y Secrets
**Archivo**: [k8s/configmap.yaml](../k8s/configmap.yaml)

**ConfigMap**:
- `DB_PATH`: `/data/tasks.db`
- `LOG_LEVEL`: `INFO`
- `FLASK_ENV`: `production`

**Secret** (placeholder):
- Estructura para secretos
- ⚠️ NO comprometer credenciales reales en git

#### 5. Validación mejorada — app.py
**Archivo**: [src/app.py](../src/app.py)

**POST /tasks**:
- ✅ Validar título no vacío
- ✅ Límite: 255 caracteres máximo
- ✅ Límite descripción: 1000 caracteres
- ✅ Error handling mejorado (try-catch)
- ✅ Logs de auditoría (task created/failed)

**PUT /tasks/<id>**:
- ✅ Validación de campos
- ✅ Mensajes de error específicos
- ✅ Logging de acciones

#### 6. CI/CD — GitHub Actions mejorado
**Archivo**: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)

- ✅ Tags de imagen: latest + SHA
- ✅ Retention de artefactos: 30 días

#### 7. Configuración de linting
**Archivo**: [.flake8](.flake8)

```
Max line length: 100
Excluye: __pycache__, .venv, build, dist
Reglas específicas por archivo
```

#### 8. Pre-commit hooks
**Archivo**: [.pre-commit-config.yaml](.pre-commit-config.yaml)

Hooks automáticos antes de commit:
- ✅ YAML validation
- ✅ Trailing whitespace
- ✅ Flake8 (linting)
- ✅ Isort (import sorting)
- ✅ Black (formatting)
- ✅ Bandit (security checks)

#### 9. Security scanning — Bandit
**Archivo**: [.bandit](.bandit)

Configuración para análisis de seguridad estática.

#### 10. Documentación — Kubernetes
**Archivo**: [k8s/README.md](../k8s/README.md)

Guía de despliegue con:
- Requisitos
- Pasos rápidos
- Health checks
- Troubleshooting
- Escalado

#### 11. Documentación — Grafana Export
**Archivo**: [docs/grafana-export-guide.md](../docs/grafana-export-guide.md)

Guía para:
- Exportar dashboards como JSON
- Importar en diferentes entornos
- Paneles recomendados con PromQL
- Alertas sugeridas
- Buenas prácticas

---

### 📊 Resumen de cambios

| Área | Antes | Después |
|------|-------|---------|
| Docker | User: root | User: appuser (no-root) |
| K8s | emptyDir | PersistentVolumeClaim |
| K8s | No probes | livenessProbe + readinessProbe |
| K8s | Sin limits | Requests/Limits definidos |
| Validación | Básica | Mejorada + logging |
| CI/CD | 1 tag (SHA) | 2 tags (SHA + latest) |
| Config files | Ninguno | .flake8, .pre-commit-config.yaml, .bandit |
| Docs | Parcial | Completa (K8s, Grafana) |

---

### 🚀 Cómo verificar los cambios

#### 1. Dockerfile (usuario no-root)
```bash
docker build -t todo-api:test .
docker run --rm todo-api:test id
# Debe mostrar uid=1000
```

#### 2. Validación (app.py)
```bash
python -m pytest -v tests/test_app.py::test_create_task
```

#### 3. Kubernetes
```bash
kubectl apply -f k8s/
kubectl get pods -l app=todo-api
kubectl describe pod <pod-name>  # Revisar probes
```

#### 4. Pre-commit hooks
```bash
# Instalar
pip install pre-commit
pre-commit install

# Probar
pre-commit run --all-files
```

#### 5. Linting
```bash
flake8 src tests
bandit -r src/
```

---

### 📈 Impacto esperado

**Seguridad** 🔒:
- Reducción de vulnerabilidades (usuario no-root)
- Validación mejorada de inputs
- Security scanning pre-commit

**Confiabilidad** 🛡️:
- Health probes → detección automática de fallos
- Persistencia → no pérdida de datos
- Resource limits → evita saturación

**Mantenibilidad** 📚:
- Documentación completa
- Pre-commit hooks → mejor código
- Configuración explícita

**DevOps** 🚀:
- K8s listo para producción
- Dashboards reproducibles
- CI/CD mejorado

---

### 🔄 Próximos pasos (opcionales)

- [ ] Publicar imagen a DockerHub/GHCR
- [ ] Agregar Helm chart
- [ ] Implementar Sealed Secrets
- [ ] ConfigMap dinámico (Kustomize)
- [ ] Ingress controller
- [ ] Network policies
- [ ] Pod Disruption Budgets
- [ ] Horizontal Pod Autoscaler (HPA)

---

**Generado**: 2026-05-26  
**Estado**: ✅ Implementación completa
