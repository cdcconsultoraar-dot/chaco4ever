@echo off
chcp 65001 >nul
title Subir TODO el proyecto a GitHub (incluye la automatizacion)
cd /d "C:\backup claude\Proyecto Chaco For Ever"

echo ============================================================
echo   SUBIENDO TODO EL PROYECTO A GITHUB
echo   (paneles + scripts + workflow de automatizacion)
echo   Repo: github.com/cdcconsultoraar-dot/chaco4ever
echo ============================================================
echo.

del ".git\HEAD.lock"  2>nul
del ".git\index.lock" 2>nul

echo [1/3] Agregando todos los cambios...
git add -A

echo [2/3] Creando el commit...
git commit -m "Setup automatizacion diaria (GitHub Actions) + paneles al dia"

echo [3/3] Subiendo a GitHub (push)...
git push origin main

echo.
echo ============================================================
echo   Si arriba ves  "main -> main"  = subido OK.
echo   Ahora, en GitHub -> Settings -> Actions -> General:
echo   pone "Read and write permissions" y guarda.
echo   Despues, pestana Actions -> Run workflow para probarlo.
echo ============================================================
echo.
pause
