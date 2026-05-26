# Pipeline CI/CD

El pipeline de GitHub Actions está en `.github/workflows/ci-cd.yml` y realiza lo siguiente:

1. `checkout` del código fuente
2. configuración de Python 3.11
3. instalación de dependencias de runtime y dev
4. auditoría de dependencias con `pip-audit`
5. linting con `flake8`
6. ejecución de pruebas unitarias con `pytest`
7. construcción de la imagen Docker
8. generación de artefactos de build en `reports/`

Esto permite validar la aplicación, generar reportes y construir una imagen versionada en cada push o PR.
