#!/usr/bin/env python3
"""
MCP "chaco-deploy" — publica el panel Chaco For Ever directo al repo de GitHub.
Hace UN commit con los archivos indicados usando la API de GitHub (Git Data API),
y como Netlify esta conectado al repo, el sitio se actualiza solo.

Config por variables de entorno (se setean en la config de Claude, ver README):
  GITHUB_TOKEN   (obligatorio)  token personal de GitHub con permiso Contents: Read and write
  GITHUB_REPO    (opcional)     "owner/repo"  -> por defecto cdcconsultoraar-dot/chaco4ever
  GITHUB_BRANCH  (opcional)     rama          -> por defecto main
  PROJECT_DIR    (opcional)     carpeta local -> por defecto C:\\backup claude\\Proyecto Chaco For Ever

Solo usa la libreria estandar de Python + el paquete "mcp".
"""
import os
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, List

from fastmcp import FastMCP

API = "https://api.github.com"
DEFAULT_REPO = "cdcconsultoraar-dot/chaco4ever"
DEFAULT_DIR = r"C:\backup claude\Proyecto Chaco For Ever"
DEFAULT_FILES = [
    "index.html",
    "Panel_Permanencia_CFE_2026.html",
    "Panel_Permanencia_CFE_2026_WhatsApp.html",
]

mcp = FastMCP("chaco-deploy")


def _cfg():
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPO", DEFAULT_REPO).strip()
    branch = os.environ.get("GITHUB_BRANCH", "main").strip()
    proj = os.environ.get("PROJECT_DIR", DEFAULT_DIR)
    return token, repo, branch, proj


def _gh(method: str, path: str, token: str, body=None):
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "chaco-deploy-mcp")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        hint = ""
        if e.code == 401:
            hint = " -> El token es invalido o vencio. Genera uno nuevo (Contents: Read and write)."
        elif e.code == 403:
            hint = " -> El token no tiene permiso sobre este repo (falta Contents: Read and write)."
        elif e.code == 404:
            hint = " -> Repo o rama no encontrados. Revisa GITHUB_REPO y GITHUB_BRANCH."
        elif e.code == 409:
            hint = " -> Conflicto: alguien mas pusheo. Volve a intentar."
        raise RuntimeError(f"GitHub {e.code} en {method} {path}:{hint}\n{detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"No se pudo conectar a GitHub: {e}")


@mcp.tool()
def estado() -> str:
    """Muestra el ultimo commit publicado en el repo (solo lectura). Sirve para verificar que version esta arriba."""
    token, repo, branch, _ = _cfg()
    if not token:
        return "ERROR: falta GITHUB_TOKEN en la configuracion del MCP."
    ref = _gh("GET", f"/repos/{repo}/git/ref/heads/{branch}", token)
    sha = ref["object"]["sha"]
    c = _gh("GET", f"/repos/{repo}/git/commits/{sha}", token)
    msg = c.get("message", "")
    date = c.get("committer", {}).get("date", "")
    return f"Repo {repo}@{branch}\nUltimo commit: {sha[:7]}\nFecha: {date}\nMensaje: {msg}"


@mcp.tool()
def publicar(mensaje: str = "Actualizacion del panel Chaco For Ever",
             archivos: Optional[List[str]] = None) -> str:
    """
    Publica los archivos del panel al repo de GitHub en UN commit (Netlify redeploya solo).

    Args:
        mensaje: texto del commit.
        archivos: lista de rutas relativas a PROJECT_DIR. Si se omite, publica los 3 paneles
                  (index.html, Panel_Permanencia_CFE_2026.html y la version WhatsApp).
    """
    token, repo, branch, proj = _cfg()
    if not token:
        return "ERROR: falta GITHUB_TOKEN en la configuracion del MCP. Ver README para generarlo."
    files = archivos if archivos else list(DEFAULT_FILES)

    # Validar que existan localmente
    faltan = [f for f in files if not os.path.isfile(os.path.join(proj, f))]
    if faltan:
        return (f"ERROR: no encuentro estos archivos en {proj}: {', '.join(faltan)}. "
                f"Revisa PROJECT_DIR o los nombres.")

    # 1) commit base y su arbol
    ref = _gh("GET", f"/repos/{repo}/git/ref/heads/{branch}", token)
    base_sha = ref["object"]["sha"]
    base_commit = _gh("GET", f"/repos/{repo}/git/commits/{base_sha}", token)
    base_tree = base_commit["tree"]["sha"]

    # 2) crear un blob por archivo
    tree_entries = []
    for rel in files:
        with open(os.path.join(proj, rel), "rb") as fh:
            content = fh.read()
        blob = _gh("POST", f"/repos/{repo}/git/blobs", token,
                   {"content": base64.b64encode(content).decode(), "encoding": "base64"})
        tree_entries.append({
            "path": rel.replace("\\", "/"),
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })

    # 3) arbol nuevo, 4) commit, 5) mover la rama
    tree = _gh("POST", f"/repos/{repo}/git/trees", token,
               {"base_tree": base_tree, "tree": tree_entries})
    commit = _gh("POST", f"/repos/{repo}/git/commits", token,
                 {"message": mensaje, "tree": tree["sha"], "parents": [base_sha]})
    _gh("PATCH", f"/repos/{repo}/git/refs/heads/{branch}", token, {"sha": commit["sha"]})

    return (f"OK - Publicado en {repo}@{branch}\n"
            f"Commit: {commit['sha'][:7]} ({len(files)} archivos)\n"
            f"{commit.get('html_url', '')}\n"
            f"Netlify redeploya solo en 1-2 minutos.")


if __name__ == "__main__":
    mcp.run()
