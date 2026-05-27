# Pipeline CI/CD

## Qué hace
- Ejecuta linting con `flake8`.
- Ejecuta tests con `pytest`.
- Audita dependencias con `pip-audit`.
- Construye imagen Docker con `docker/build-push-action`.
- Empaqueta imagen como TAR y sube artefactos.

## Requisitos para correr
- Docker instalado.
- GitHub Actions habilitado en el repositorio.
- Archivo `.github/workflows/ci-cd.yml` presente.
- `requirements-dev.txt` con `pytest`, `flake8`, `pip-audit`.

## Cómo validar localmente
1. Instalar dependencias de desarrollo:
```bash
pip install -r requirements-dev.txt
```
2. Correr lint:
```bash
python -m flake8 src tests
```
3. Correr tests:
```bash
python -m pytest tests/ -v
```
4. Correr auditoría:
```bash
python -m pip_audit
```
5. Construir Docker local:
```bash
docker build -t todo-api:latest .
```

## Artefactos generados
- `reports/junit.xml`
- `reports/todo-api-<sha>.tar`
- artifacts de GitHub Actions (`test-reports`, `docker-image`).
