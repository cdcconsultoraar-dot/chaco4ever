#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actualiza la tabla de la Zona A (Primera Nacional) en los 3 paneles HTML de
Chaco For Ever a partir de la clasificacion publica de BeSoccer.

Pensado para correr en GitHub Actions (una vez por dia). Es "fail-safe":
si no logra parsear las 18 filas de la Zona A o no encuentra a Chaco For Ever,
NO toca ningun archivo (para no publicar datos rotos).

Actualiza, en index.html + los dos paneles:
  - el array  const tabla=[...]  (posiciones, PJ/G/E/P/GF/GC/DG/Pts + Ultimos 5)
  - el subtitulo del header (posicion de For Ever + fecha de actualizacion)
  - el badge "HOY: ..." (dentro / fuera de la zona)
  - el KPI de Posicion (valor y color)

Los textos de analisis (destacado, escenarios) NO se tocan: son editoriales.
"""
import re
import sys
import io
import datetime
import urllib.request

import pandas as pd

URL = "https://es.besoccer.com/competicion/clasificacion/primera_b_nacional/2026/grupo1"
FILES = [
    "index.html",
    "Panel_Permanencia_CFE_2026.html",
    "Panel_Permanencia_CFE_2026_WhatsApp.html",
]

# substring detectado en la web  ->  nombre que usa el panel
NAME_MAP = [
    ("Ferro", "Ferro Carril Oeste"),
    ("Morón", "Deportivo Morón"), ("Moron", "Deportivo Morón"),
    ("Colón", "Colón (SF)"), ("Colon", "Colón (SF)"),
    ("Almirante Brown", "Almirante Brown"),
    ("Godoy Cruz", "Godoy Cruz"),
    ("Madryn", "Deportivo Madryn"),
    ("Bolívar", "Ciudad de Bolívar"), ("Bolivar", "Ciudad de Bolívar"),
    ("Los Andes", "Los Andes"),
    ("Estudiantes", "Estudiantes (BA)"),
    ("Racing", "Racing (Córdoba)"),
    ("Mitre", "Mitre (SdE)"),
    ("San Miguel", "San Miguel"),
    ("Belgrano", "Def. de Belgrano"),
    ("All Boys", "All Boys"),
    ("San Telmo", "San Telmo"),
    ("Central Norte", "Central Norte"),
    ("Chaco For Ever", "CHACO FOR EVER"),
    ("Acassuso", "Acassuso"),
]


def log(msg):
    print(f"[update_panel] {msg}", flush=True)


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def map_name(cell_text):
    for sub, name in NAME_MAP:
        if sub.lower() in cell_text.lower():
            return name
    return None


def first_int(x):
    m = re.search(r"-?\d+", str(x))
    return int(m.group()) if m else None


def extract_form(cell_text):
    """Toma los ultimos 3-5 tokens V/E/D del final del texto de la celda del equipo."""
    m = re.search(r"((?:[VED]\s+){2,4}[VED])\s*$", cell_text.strip())
    if not m:
        return None
    letters = re.findall(r"[VED]", m.group(1))
    conv = {"V": "W", "E": "E", "D": "L"}
    return "".join(conv[c] for c in letters[-5:])


def pick_zona_a(tables):
    for df in tables:
        try:
            flat = df.astype(str)
        except Exception:
            continue
        has_cfe = flat.apply(lambda col: col.str.contains("Chaco For Ever", case=False, na=False)).any().any()
        cols = [str(c) for c in df.columns]
        has_pts = any(c.strip() == "Pts" for c in cols) or "Pts" in " ".join(cols)
        if has_cfe and has_pts and len(df) >= 18:
            return df
    return None


def col_named(df, name):
    for c in df.columns:
        if str(c).strip() == name or str(c).strip().endswith(name):
            return c
    return None


def team_column(df):
    for c in df.columns:
        if df[c].astype(str).str.contains("Chaco For Ever", case=False, na=False).any():
            return c
    return None


def parse_table(html):
    tables = pd.read_html(io.StringIO(html))
    df = pick_zona_a(tables)
    if df is None:
        raise RuntimeError("No encontre la tabla de la Zona A con las 18 filas.")
    tcol = team_column(df)
    cols = {k: col_named(df, k) for k in ["Pts", "PJ", "PG", "PE", "PP", "GF", "GC"]}
    if tcol is None or any(v is None for v in cols.values()):
        raise RuntimeError(f"Faltan columnas. team={tcol} cols={cols}")

    rows = []
    pos = 0
    for _, r in df.iterrows():
        cell = str(r[tcol])
        name = map_name(cell)
        if not name:
            continue
        pos += 1
        rows.append({
            "pos": pos,
            "name": name,
            "pj": first_int(r[cols["PJ"]]),
            "g": first_int(r[cols["PG"]]),
            "e": first_int(r[cols["PE"]]),
            "p": first_int(r[cols["PP"]]),
            "gf": first_int(r[cols["GF"]]),
            "gc": first_int(r[cols["GC"]]),
            "pts": first_int(r[cols["Pts"]]),
            "form": extract_form(cell),
        })
    return rows


def tag_for(pos, is_cfe):
    if is_cfe:
        return ("d", "ZONA ROJA") if pos >= 17 else ("ok", "A FLOTE")
    if pos == 1:
        return ("ok", "Ascenso")
    if 2 <= pos <= 8:
        return ("ok", "Reducido")
    if 9 <= pos <= 13:
        return ("ok", "Mitad")
    if 14 <= pos <= 16:
        return ("p", "Peligro")
    return ("d", "DESCIENDE")


def dg_str(gf, gc):
    d = gf - gc
    return "+%d" % d if d > 0 else ("0" if d == 0 else str(d))


def old_forms(html):
    m = re.search(r"const tabla=\[(.*?)\]\];", html, re.S)
    out = {}
    if not m:
        return out
    for row in re.findall(r'\[\d+,"([^"]+)",[^\]]*"([A-Z]{0,5})"\]', m.group(1)):
        out[row[0]] = row[1]
    return out


def build_tabla(rows, prev_forms):
    lines = []
    for r in rows:
        is_cfe = r["name"] == "CHACO FOR EVER"
        cls, tag = tag_for(r["pos"], is_cfe)
        form = r["form"] or prev_forms.get(r["name"], "")
        lines.append('[%d,"%s",%d,%d,%d,%d,%d,%d,"%s",%d,"%s","%s","%s"]' % (
            r["pos"], r["name"], r["pj"], r["g"], r["e"], r["p"],
            r["gf"], r["gc"], dg_str(r["gf"], r["gc"]), r["pts"], cls, tag, form))
    return "const tabla=[\n" + ",\n".join(lines) + "];"


def main():
    html0 = fetch(URL)
    rows = parse_table(html0)

    if len(rows) != 18:
        log(f"ABORTO: parsee {len(rows)} equipos (esperaba 18). No modifico nada.")
        return 0
    cfe = next((r for r in rows if r["name"] == "CHACO FOR EVER"), None)
    if not cfe:
        log("ABORTO: no encontre a Chaco For Ever. No modifico nada.")
        return 0
    # chequeo de integridad basico
    for r in rows:
        if None in (r["pj"], r["g"], r["e"], r["p"], r["gf"], r["gc"], r["pts"]):
            log(f"ABORTO: datos incompletos en {r['name']}. No modifico nada.")
            return 0
        if r["g"] + r["e"] + r["p"] != r["pj"] or r["g"] * 3 + r["e"] != r["pts"]:
            log(f"ABORTO: no cierran los numeros de {r['name']}. No modifico nada.")
            return 0

    now_ar = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    fecha = now_ar.strftime("%d/%m/%Y")
    stamp_val = now_ar.strftime("%d/%m/%Y %H:%M")
    pos, pts, pj = cfe["pos"], cfe["pts"], cfe["pj"]
    in_zone = pos >= 17

    new_sub = ('<p>Primera Nacional · Zona A · For Ever %d° (%d pts) · Proyecto Forever 2031</p>' % (pos, pts))
    if in_zone:
        new_badge = '<span class="badge">HOY: %d° — EN ZONA DE DESCENSO</span>' % pos
    else:
        new_badge = '<span class="badge up">HOY: %d° — FUERA DE LA ZONA DE DESCENSO</span>' % pos
    kcls = "rojo" if in_zone else ("amar" if pos >= 15 else "verde")
    new_kpi = ('<div class="kpi %s"><div class="v">%d°</div>'
               '<div class="l">Posición (%d pts, %d PJ)</div></div>' % (kcls, pos, pts, pj))

    changed_any = False
    for f in FILES:
        with io.open(f, encoding="utf-8") as fh:
            html = fh.read()
        prev = old_forms(html)
        new_tabla = build_tabla(rows, prev)

        new = re.sub(r"const tabla=\[.*?\]\];", lambda m: new_tabla, html, count=1, flags=re.S)
        new = re.sub(r"<p>Primera Nacional · Zona A.*?Proyecto Forever 2031</p>",
                     lambda m: new_sub, new, count=1, flags=re.S)
        new = re.sub(r'<span class="badge[^"]*">HOY:[^<]*</span>',
                     lambda m: new_badge, new, count=1)
        new = re.sub(r'<div class="kpi \w+"><div class="v">\d+°</div><div class="l">Posición[^<]*</div></div>',
                     lambda m: new_kpi, new, count=1)
        new = re.sub(r'(<b id="lastUpdate">).*?(</b>)',
                     lambda m: m.group(1) + stamp_val + m.group(2), new, count=1, flags=re.S)

        if new != html:
            with io.open(f, "w", encoding="utf-8") as fh:
                fh.write(new)
            changed_any = True
            log(f"actualizado {f}")
        else:
            log(f"sin cambios {f}")

    log(f"For Ever: {pos}° · {pts} pts · {pj} PJ · {'EN ZONA' if in_zone else 'fuera de zona'} · {fecha}")
    log("LISTO" if changed_any else "Nada que actualizar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
