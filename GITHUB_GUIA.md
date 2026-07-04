# Guía GitHub — Nivel alto (5 módulos)

Desarrollo individual simulando colaboración equilibrada entre **5 módulos**.

## Paso 1: Crear repositorio

1. GitHub → **New repository** → nombre: `software-fj-gestion`
2. En PowerShell:

```powershell
cd "C:\Users\kathe\Documents\Escritorio\tareas UNAD\Programacion\Fase 4"
git init
git branch -M main
git remote add origin https://github.com/TU_USUARIO/software-fj-gestion.git
git add README.md .gitignore
git commit -m "docs: inicializar repositorio del proyecto"
git push -u origin main
```

## Paso 2: Crear 5 issues

Usar textos de `ISSUES.md`. Asignarlos a tu usuario (simula 5 integrantes = 5 módulos).

## Paso 3: Subir por módulos

Repetir para cada módulo:

```powershell
git checkout main
git pull
git checkout -b feature/NOMBRE-RAMA
git add ARCHIVOS_DEL_MODULO
git commit -m "feat: descripción clara del cambio"
git push -u origin feature/NOMBRE-RAMA
```

En GitHub: **Pull Request** → descripción con `Closes #N` → **Merge**.

| Módulo | Rama | Issue |
|--------|------|-------|
| 1 | `feature/base-y-excepciones` | #1 |
| 2 | `feature/modulo-clientes` | #2 |
| 3 | `feature/modulo-servicios` | #3 |
| 4 | `feature/modulo-reservas` | #4 |
| 5 | `feature/interfaz-y-documentacion` | #5 |

## Paso 4: Verificar nivel alto

- [ ] 5 ramas con commits descriptivos
- [ ] 5 pull requests fusionados
- [ ] 5 issues cerrados
- [ ] README visible en el repo
- [ ] Historial con merges a `main`
