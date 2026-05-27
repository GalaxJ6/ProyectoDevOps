# Kubernetes Deployment Guide

Manifests para desplegar la To-Do API en Kubernetes.

## Contenidos

| Archivo | Descripción |
|---------|-------------|
| `deployment.yaml` | Deployment con 2 replicas, health probes, resource limits |
| `service.yaml` | Service ClusterIP para acceso interno |
| `persistentvolumeclaim.yaml` | PVC para persistencia de datos (SQLite) |
| `configmap.yaml` | ConfigMap y Secret para variables de entorno |

## Requisitos

- Cluster Kubernetes (v1.20+)
- `kubectl` configurado
- Imagen Docker `todo-api:latest` disponible localmente o en un registry

## Uso local con Minikube / Kind

### 0. Construir la imagen Docker
```bash
docker build -t todo-api:latest .
```

### 1. Cargar la imagen en el cluster local

#### Con Minikube
```bash
minikube image load todo-api:latest
```

#### Con Kind
```bash
kind load docker-image todo-api:latest
```

Si usas un cluster remoto, sube la imagen a un registry y actualiza `image:` en `k8s/deployment.yaml`.

## Despliegue rápido

### 1. Crear namespace (opcional)
```bash
kubectl create namespace todo-api
```

### 2. Aplicar manifests
```bash
# Desplegar en namespace default
kubectl apply -f k8s/

# O en namespace específico
kubectl apply -f k8s/ -n todo-api
```

### 3. Verificar despliegue
```bash
# Ver pods
kubectl get pods -l app=todo-api

# Ver detalles de deployment
kubectl describe deployment todo-api

# Ver logs
kubectl logs -l app=todo-api -f

# Ver service
kubectl get svc todo-api
```

### 4. Acceder a la API

#### Port-Forward (desarrollo)
```bash
kubectl port-forward svc/todo-api 5000:5000
```

Luego acceder a `http://localhost:5000`

#### Ingress (producción)
Crear un Ingress resource para exposición HTTP/HTTPS.

## Health Checks

La API expone el endpoint `/health` que Kubernetes utiliza para:

- **Liveness Probe**: Detecta pods muertos (reinicia si falla 3 veces en 30 seg)
- **Readiness Probe**: Detecta si la app está lista (remueve del balancer si falla 2 veces en 15 seg)

## Persistencia

- **PVC**: `todo-api-pvc` (1Gi)
- **Montaje**: `/data/tasks.db`
- **Clase de almacenamiento**: `standard` (ajustar según cluster)

Para usar persistencia diferente (EBS, NFS, etc.), editar `persistentvolumeclaim.yaml`.

## Seguridad

- ✅ Usuario no-root (`appuser`)
- ✅ Resource limits (requests/limits)
- ✅ Health probes
- 🟡 Secrets (usar Sealed Secrets o Vault en producción)

## Escalado

Cambiar replicas en `deployment.yaml`:
```yaml
spec:
  replicas: 3  # aumentar según carga
```

Luego reapllicar:
```bash
kubectl apply -f k8s/deployment.yaml
```

## Troubleshooting

### Pods en estado Pending
```bash
kubectl describe pod <pod-name>
# Revisar events
```

### Logs de error
```bash
kubectl logs <pod-name>
```

### Revisar recursos disponibles
```bash
kubectl top nodes
kubectl top pods -l app=todo-api
```

---

**Referencias**:
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Health Checks Best Practices](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
