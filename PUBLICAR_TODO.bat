@echo off
chcp 65001 >nul
title Publicar TODO en GitHub (resuelve divergencias)
cd /d "C:\backup claude\Proyecto Chaco For Ever"

echo ============================================================
echo   PUBLICANDO EN GITHUB (paneles + automatizacion)
echo   Repo: github.com/cdcconsultoraar-dot/chaco4ever
echo ============================================================
echo.

del ".git\HEAD.lock"  2>nul
del ".git\index.lock" 2>nul

rem  Asegura modo "merge" (no rebase) para el pull
git config pull.rebase false

echo [1/4] Guardando tus cambios en un commit...
git add -A
git commit -m "Panel al dia + automatizacion diaria" 2>nul

echo [2/4] Trayendo lo que haya en GitHub y conservando TU version...
git pull --no-edit -X ours origin main

echo [3/4] Subiendo a GitHub...
git push origin main

echo [4/4] Estado final:
git status -sb

echo.
echo ============================================================
echo   Si en el paso 3 NO ves la palabra "rejected", quedo OK.
echo   Netlify (chaco4ever.netlify.app) se actualiza en 1-2 min.
echo.
echo   Si ves "rejected" o pide usuario/token, copiame TODO lo
echo   que aparece en esta ventana y te lo resuelvo.
echo ============================================================
echo.
pause
