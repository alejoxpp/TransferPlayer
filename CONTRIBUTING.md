# 🤝 Contributing a TransferPlayer

¡Gracias por tu interés en contribuir! Sigue estas pautas para mantener el
proyecto limpio y de calidad.

## Flujo de trabajo

1. **Fork** del repositorio.
2. Crea una rama de trabajo:
   ```bash
   git checkout -b feat/mi-feature
   ```
   Convención: `feat/`, `fix/`, `refactor/`, `docs/`, `chore/`.
3. Haz cambios pequeños y con **commits convencionales**:
   ```bash
   git commit -m "feat: añade filtro por temporada"
   ```
4. Ejecuta las comprobaciones de calidad antes del push:
   ```bash
   ruff check transferplayer tests
   black --check transferplayer tests
   mypy transferplayer --ignore-missing-imports
   pytest -q
   ```
5. Abre un **Pull Request** hacia `main`. El CI verificará calidad, tests y build.

## Convenciones de código

- Python 3.11+, tipado completo (mypy estricto).
- Formato `black` (line-length 100) + `ruff`.
- Modelos Pydantic para validación; SQLAlchemy 2.0 async para la capa de datos.
- Sin secretos en el código: todo se configura vía `.env` (ver `.env.example`).

## Reportar issues

Incluye siempre: versión de Python, pasos para reproducir y salida de
consola/logs relevantes.