@echo off
chcp 65001 >nul
title Publicar Chaco For Ever en GitHub + Netlify
cd /d "C:\backup claude\Proyecto Chaco For Ever"

echo ============================================================
echo   PUBLICANDO PANEL CHACO FOR EVER (Fecha 24)
echo   Repo: github.com/cdcconsultoraar-dot/chaco4ever
echo ============================================================
echo.

rem  Quita candados viejos de git si existen
del ".git\HEAD.lock"  2>nul
del ".git\index.lock" 2>nul

echo [1/3] Agregando archivos...
git add index.html Panel_Permanencia_CFE_2026.html Panel_Permanencia_CFE_2026_WhatsApp.html

echo [2/3] Creando el commit...
git commit -m "Fecha 24: historial, Ultimos 5, detalle por partido y correccion de zona (Madryn)"

echo [3/3] Subiendo a GitHub (push)...
git push origin main

echo.
echo ============================================================
echo   Si arriba ves algo como  "main -> main"  = PUBLICADO OK.
echo   Netlify (chaco4ever.netlify.app) se actualiza solo
echo   en 1-2 minutos.
echo.
echo   Si te pidio usuario y contrasena de GitHub y fallo,
echo   avisale a Claude: hace falta un token de acceso.
echo ============================================================
echo.
pause
