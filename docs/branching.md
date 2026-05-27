# Estrategia de Branching

## Ramas principales
- `main` — rama de producción estable.
- `feature/*` — nuevas funcionalidades.
- `fix/*` — correcciones de bugs.
- `release/*` — preparaciones de release opcionales.

## Reglas
- Cada PR debe generarse desde una rama `feature/` o `fix/`.
- `main` solo recibe merges aprobados y con CI verde.
- Usar nombre claro: `feature/add-metrics`, `fix/db-connection`.

## Requisitos para correr
- Git instalado.
- Configurar protección de rama en GitHub:
  - `Require status checks to pass`
  - `Require pull request reviews`

## Flujo mínimo
```bash
git checkout -b feature/nombre
# hacer cambios
git add .
git commit -m "feature: descripcion"
git push origin feature/nombre
```

Luego abrir PR hacia `main`.
