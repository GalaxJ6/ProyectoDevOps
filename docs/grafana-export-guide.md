# Grafana Dashboard Export Guide

Guía para exportar y reutilizar dashboards de Grafana de forma reproducible.

## Cómo exportar un dashboard

### Opción 1: Exportar como JSON (recomendado)

1. **Abre tu dashboard en Grafana**
   - http://localhost:3000

2. **Haz clic en el ícono de engranaje (⚙️) en la esquina superior derecha**
   - Selecciona "Share" → "Export"

3. **Haz clic en "Save to file"**
   - Se descargará un archivo JSON

4. **Guarda el archivo en `docs/`**
   ```bash
   # Ejemplo
   mv ~/Downloads/dashboard-name.json docs/grafana-todo-api-dashboard.json
   ```

### Opción 2: Exportar desde la terminal

```bash
# Obtener ID del dashboard desde la URL
# URL: http://localhost:3000/d/abc123/dashboard-name
# ID: abc123

# Exportar usando API de Grafana
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:3000/api/dashboards/uid/abc123 \
  > docs/grafana-dashboard.json
```

## Importar dashboard

### En Grafana UI

1. Abre Grafana → Home
2. Haz clic en "+" → "Import dashboard"
3. Sube el archivo JSON o pega el contenido
4. Configura variables si es necesario

### Usando Docker Compose

Para que Grafana cargue dashboards automáticamente al iniciar:

```yaml
# En docker-compose.yml
grafana:
  image: grafana/grafana:latest
  volumes:
    - ./docs/grafana-dashboard.json:/etc/grafana/provisioning/dashboards/dashboard.json:ro
```

### Usando Kubernetes

Crear ConfigMap con el dashboard:

```bash
kubectl create configmap grafana-dashboard \
  --from-file=docs/grafana-dashboard.json \
  -n monitoring
```

Luego montar en el Deployment de Grafana.

## Estructura de un dashboard JSON

```json
{
  "annotations": {
    "list": []
  },
  "dashboard": {
    "title": "To-Do API Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "sum(rate(todo_api_requests_total[1m])) by (endpoint)"
          }
        ]
      }
    ]
  }
}
```

## Paneles recomendados para esta API

### 1. Requests por segundo
```promql
sum(rate(todo_api_requests_total[1m])) by (endpoint)
```

### 2. Latencia P50
```promql
histogram_quantile(0.5, sum(rate(todo_api_request_latency_seconds_bucket[5m])) by (le, endpoint))
```

### 3. Latencia P95
```promql
histogram_quantile(0.95, sum(rate(todo_api_request_latency_seconds_bucket[5m])) by (le, endpoint))
```

### 4. Tasa de errores (5xx)
```promql
sum(rate(todo_api_requests_total{http_status=~"5.."}[5m])) by (endpoint)
```

### 5. Errores por tipo (4xx vs 5xx)
```promql
sum(rate(todo_api_requests_total{http_status=~"[45].."}[5m])) by (http_status)
```

### 6. Uptime (disponibilidad)
```promql
up{job="todo-api"}
```

## Alertas (opcional)

Crear alertas basadas en umbrales:

```promql
# Alerta: Tasa de errores > 5%
(sum(rate(todo_api_requests_total{http_status=~"5.."}[5m])) by (endpoint) / 
 sum(rate(todo_api_requests_total[5m])) by (endpoint)) > 0.05

# Alerta: Latencia P95 > 1s
histogram_quantile(0.95, rate(todo_api_request_latency_seconds_bucket[5m])) > 1

# Alerta: Pod no disponible
up{job="todo-api"} == 0
```

## Template Variables (Grafana)

Para crear dashboards reutilizables:

```json
{
  "templating": {
    "list": [
      {
        "name": "endpoint",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(todo_api_requests_total, endpoint)"
      }
    ]
  }
}
```

## Buenas prácticas

1. ✅ **Versionado**: Guardar JSON en git
2. ✅ **Documentación**: Comentar qué mide cada panel
3. ✅ **Reutilizable**: Usar variables template
4. ✅ **Alertas**: Configurar umbrales sensatos
5. ✅ **Actualizaciones**: Exportar y re-guardar después de cambios

---

**Referencias**:
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus Queries](https://prometheus.io/docs/prometheus/latest/querying/basics/)
