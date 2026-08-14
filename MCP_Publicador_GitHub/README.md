# MCP "chaco-deploy" — publicar el panel directo a GitHub

Este MCP le permite a Claude subir los archivos del panel a tu repo
`cdcconsultoraar-dot/chaco4ever` con un solo comando. Como Netlify está
conectado a ese repo, el sitio `chaco4ever.netlify.app` se actualiza solo.

Herramientas que expone:
- **publicar** — hace un commit con los 3 paneles (o los archivos que le pases).
- **estado** — muestra el último commit publicado (para verificar).

---

## 1. Requisitos (una sola vez)

**Python 3.10 o superior.** Para chequear, abrí PowerShell y escribí:

```
python --version
```

Si no lo tenés, instalalo desde https://www.python.org/downloads/ (marcá
"Add Python to PATH" en el instalador).

Luego instalá el framework MCP:

```
pip install fastmcp
```

---

## 2. Crear tu token de GitHub (una sola vez)

1. Entrá a https://github.com/settings/tokens?type=beta (Fine-grained tokens).
2. **Generate new token.**
3. *Repository access* → **Only select repositories** → elegí **chaco4ever**.
4. *Permissions* → *Repository permissions* → **Contents: Read and write**.
5. Generá el token y **copialo** (empieza con `github_pat_...`). Solo se ve una vez.

> El token es como una contraseña: no lo compartas ni lo subas al repo.

---

## 3. Conectar el MCP a Claude (una sola vez)

Abrí el archivo de configuración de Claude Desktop / Cowork:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  (pegá esa ruta en el explorador de archivos).

Agregá el bloque `chaco-deploy` dentro de `mcpServers` (si el archivo está
vacío, pegá todo esto):

```json
{
  "mcpServers": {
    "chaco-deploy": {
      "command": "python",
      "args": ["C:\\backup claude\\Proyecto Chaco For Ever\\MCP_Publicador_GitHub\\server.py"],
      "env": {
        "GITHUB_TOKEN": "PEGA_TU_TOKEN_ACA",
        "GITHUB_REPO": "cdcconsultoraar-dot/chaco4ever",
        "GITHUB_BRANCH": "main",
        "PROJECT_DIR": "C:\\backup claude\\Proyecto Chaco For Ever"
      }
    }
  }
}
```

Reemplazá `PEGA_TU_TOKEN_ACA` por el token del paso 2.

Guardá el archivo y **cerrá y volvé a abrir Claude** (que se reinicie del todo).

---

## 4. Usarlo

Cuando esté conectado, pedile a Claude:

- **"publica el panel"** → sube los 3 archivos y hace el commit.
- **"mostrame el estado del repo"** → te dice el último commit publicado.

En ~1-2 minutos Netlify muestra la versión nueva en `chaco4ever.netlify.app`.

---

## Problemas comunes

- **"GITHUB 401"** → el token está mal o venció. Generá uno nuevo (paso 2).
- **"GITHUB 403"** → al token le falta el permiso *Contents: Read and write*.
- **"GITHUB 404"** → revisá que `GITHUB_REPO` sea `cdcconsultoraar-dot/chaco4ever`.
- **No aparece la herramienta** → verificá la ruta de `server.py` en la config y
  que Python esté instalado; reiniciá Claude por completo.
