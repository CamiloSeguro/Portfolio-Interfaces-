import streamlit as st
from lib.data import load_projects
from itertools import chain

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Portafolio — Interfaces Multimodales",
    page_icon="🎛️",
    layout="wide"
)

# -----------------------------
# ESTILOS (simple dark + cards)
# -----------------------------
st.markdown("""
<style>
:root{--bg:#0E1020;--txt:#EDEEFF;--muted:#A7A8B3;--card:#121320;--b:#1E2138;--ring:#06B6D4;}
html, body, .stApp{background:var(--bg);color:var(--txt);}
.block-container{max-width:1100px;padding-top:1rem;}

.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;}
@media(max-width:1000px){.grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:640px){.grid{grid-template-columns:1fr;}}

.card{background:var(--card);border:1px solid var(--b);border-radius:16px;overflow:hidden;
box-shadow:0 10px 20px rgba(0,0,0,.25);transition:transform .15s ease,border-color .2s ease;}
.card:hover{transform:translateY(-2px);border-color:color-mix(in srgb,var(--ring) 50%,transparent);}
.cover{aspect-ratio:16/9;width:100%;object-fit:cover;background:#0b0d1a;}
.body{padding:12px 12px 14px;}
.title{font-weight:800;margin:0 0 6px 0;font-size:1rem;}
.sub{color:var(--muted);font-size:.9rem;margin-bottom:8px;}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;}
.chip{font-size:.75rem;padding:.22rem .5rem;border-radius:999px;border:1px solid #2a2f4b;background:#1a1d33;color:#dae0ff;}
.btn{display:inline-block;font-weight:700;font-size:.9rem;color:white;border:1px solid #2a2f4b;border-radius:999px;padding:.45rem .75rem;text-decoration:none;}
.btn:hover{border-color:#3b4163;}
hr{border:none;border-top:1px solid #1b1e34;margin:.8rem 0 1rem 0;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# IMGUR: Mapa opcional (rellénalo con tus links directos)
# Formato: nombre_de_tu_yaml_cover -> "https://i.imgur.com/XXXXXXX.jpg"
# Si usas campo cover_imgur directamente en el YAML, NO necesitas este mapa.
# -----------------------------
IMGUR_MAP = {
    # "entrega_01.png": "https://i.imgur.com/ABCDE01.jpg",
    # "assets/covers/entrega_03.jpg": "https://i.imgur.com/ABCDE03.jpg",
}

IMGUR_PLACEHOLDER = "https://i.imgur.com/U2p7Z3W.jpg"  # cámbialo si quieres

def resolve_imgur_cover(p: dict) -> str:
    """
    Prioriza:
      1) p['cover_imgur'] si está en el YAML
      2) IMGUR_MAP[ p['cover'] ]
      3) Si p['cover'] ya es un link directo de Imgur (i.imgur.com/...), úsalo
      4) Placeholder
    """
    url = (p.get("cover_imgur") or "").strip()
    if url.startswith("https://i.imgur.com/"):
        return url
    cover_key = (p.get("cover") or "").strip()
    if cover_key in IMGUR_MAP:
        return IMGUR_MAP[cover_key]
    if cover_key.startswith("https://i.imgur.com/"):
        return cover_key
    return IMGUR_PLACEHOLDER

# -----------------------------
# DATA
# -----------------------------
def get_projects():
    data = load_projects()
    for p in data:
        # defaults y normalización
        p.setdefault("title", "Proyecto sin título")
        p.setdefault("slug", "")
        p.setdefault("year", 0)
        p.setdefault("week", 0)
        p.setdefault("modality", [])
        p.setdefault("device", "")
        p.setdefault("type", "")
        p.setdefault("cover", "")        # legacy (nombre de archivo)
        p.setdefault("cover_imgur", "")  # NUEVO (link directo Imgur)
        p.setdefault("links", {})        # para leer links.demo
    return data

projects = get_projects()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("# Portafolio — **Interfaces Multimodales**")
st.caption("Universidad EAFIT · Camilo Seguro · 15 entregas")
st.divider()

# -----------------------------
# FILTROS BÁSICOS
# -----------------------------
col1, col2, col3 = st.columns([2,1,1])
with col1:
    q = st.text_input("Buscar", placeholder="Ej: voz, gestos, Quest, semana 6").strip().lower()
with col2:
    mods = sorted(set(m for p in projects for m in p.get("modality", [])))
    sel_mod = st.selectbox("Modalidad", ["(Todas)"] + mods, index=0)
with col3:
    years = sorted({p.get("year",0) for p in projects if p.get("year")}, reverse=True)
    sel_year = st.selectbox("Año", ["(Todos)"] + [str(y) for y in years], index=0)

# -----------------------------
# FILTRADO
# -----------------------------
def match(p):
    text = " ".join([
        p.get("title",""),
        " ".join(p.get("modality",[])),
        p.get("device",""),
        str(p.get("week","")),
        str(p.get("year","")),
        p.get("type","")
    ]).lower()
    if q and not all(tok in text for tok in q.split()):
        return False
    if sel_mod != "(Todas)" and sel_mod not in p.get("modality", []):
        return False
    if sel_year != "(Todos)" and str(p.get("year",0)) != sel_year:
        return False
    return True

filtered = [p for p in projects if match(p)]
filtered.sort(key=lambda p: (p.get("year",0), p.get("week",0)), reverse=True)

st.markdown(f"**{len(filtered)} proyectos encontrados**")
st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# GRID (usa SOLO Imgur) + link a páginas Streamlit
# -----------------------------
if not filtered:
    st.info("No hay resultados. Cambia los filtros o limpia la búsqueda.")
else:
    st.markdown("<div class='grid'>", unsafe_allow_html=True)
    for p in filtered:
        cover = resolve_imgur_cover(p)
        title = p.get("title")
        sub = f"{', '.join(p.get('modality', []))} · Semana {p.get('week')} · {p.get('year')}"
        chips = "".join(f"<span class='chip'>{m}</span>" for m in p.get("modality", []))
        if p.get("device"): chips += f"<span class='chip'>🎯 {p.get('device')}</span>"
        if p.get("type"):   chips += f"<span class='chip'>📦 {p.get('type')}</span>"

        # ⬇️ AHORA: usa el link de Streamlit desde tu YAML (links.demo)
        detail = p.get("links", {}).get("demo", "#")

        st.markdown(f"""
        <div class="card">
          <img class="cover" src="{cover}" alt="{title}" loading="lazy" referrerpolicy="no-referrer"/>
          <div class="body">
            <div class="title">{title}</div>
            <div class="sub">{sub}</div>
            <div class="chips">{chips}</div>
            <a class="btn" href="{detail}" target="_blank" rel="noopener">Ver detalle →</a>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# NOTA
# -----------------------------
st.caption("💡 El botón 'Ver detalle' abre el enlace de `links.demo` (página de Streamlit de cada entrega). Usa `cover_imgur` o el `IMGUR_MAP` para las portadas.")
