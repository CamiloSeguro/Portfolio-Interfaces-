import re
import streamlit as st
from lib.data import load_projects

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Portafolio — Interfaces Multimodales",
    page_icon="🎛️",
    layout="wide"
)

# -----------------------------
# ESTILOS (limpio y minimalista)
# -----------------------------
st.markdown("""
<style>
:root{
  --bg:#0E1020; --txt:#EDEEFF; --muted:#A7A8B3; --card:#121320;
  --b:#1E2138; --ring:#6a8bff;
}
html, body, .stApp{background:var(--bg);color:var(--txt);}
.block-container{max-width:1100px;padding-top:1rem;}

/* GRID compacto y responsivo */
/* === Cards uniformes === */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(0,0,0,.25);
  transition: transform .15s ease, border-color .2s ease, box-shadow .2s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 👈 Fuerza que el botón quede al fondo */
  height: 100%;
  min-height: 320px; /* 👈 asegura altura consistente */
}
.card:hover {
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--ring) 60%, transparent);
  box-shadow: 0 14px 28px rgba(106,139,255,.25);
}

.cover {
  width: 100%;
  height: 150px;
  object-fit: cover;
  background: #0b0d1a;
}

.body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 👈 distribuye el contenido */
  padding: 14px;
}

.title {
  font-weight: 800;
  font-size: .96rem;
  margin-bottom: 6px;
  color: white;
}

.summary {
  color: var(--muted);
  font-size: .85rem;
  line-height: 1.3;
  flex-grow: 1; /* 👈 llena el espacio central */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Botón siempre igual */
.actions {
  margin-top: 12px;
}
.btn {
  display: block;
  width: 100%;
  text-align: center;
  font-weight: 700;
  font-size: .9rem;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: .55rem 0;
  background: linear-gradient(120deg, #536dff, #8a5bff);
  text-decoration: none;
  transition: transform .15s ease, filter .2s ease;
}
.btn:hover {
  filter: brightness(1.1);
  transform: translateY(-2px);
}
.btn.secondary {
  background: rgba(255,255,255,.08);
  color: #cfd6ff;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
IMGUR_PLACEHOLDER = "https://i.imgur.com/U2p7Z3W.jpg"

def resolve_imgur_cover(p: dict) -> str:
    url = (p.get("cover_imgur") or "").strip()
    if url.startswith("https://i.imgur.com/"): return url
    cover = (p.get("cover") or "").strip()
    if cover.startswith("https://i.imgur.com/"): return cover
    return IMGUR_PLACEHOLDER

def minify_html(s: str) -> str:
    s = re.sub(r">\s+<", "><", s.strip())
    s = re.sub(r"\s{2,}", " ", s)
    return s

# -----------------------------
# DATA
# -----------------------------
def get_projects():
    data = load_projects()
    for p in data:
        p.setdefault("title", "Proyecto sin título")
        p.setdefault("summary", "")
        p.setdefault("links", {})
    return data

projects = get_projects()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("# Portafolio — **Interfaces Multimodales**")
st.caption(f"Universidad EAFIT · Camilo Seguro · {len(projects)} entregas")
st.divider()

# -----------------------------
# FILTROS
# -----------------------------
col1, col2 = st.columns([2,1])
with col1:
    q = st.text_input("Buscar").strip().lower()
with col2:
    years = sorted({p.get("year",0) for p in projects if p.get("year")}, reverse=True)
    sel_year = st.selectbox("Año", ["(Todos)"] + [str(y) for y in years], index=0)

def match(p):
    haystack = " ".join([
        p.get("title",""), p.get("summary",""), str(p.get("year","")), p.get("slug","")
    ]).lower()
    if q and not all(tok in haystack for tok in q.split()): return False
    if sel_year != "(Todos)" and str(p.get("year",0)) != sel_year: return False
    return True

filtered = [p for p in projects if match(p)]
filtered.sort(key=lambda p: (p.get("year",0), p.get("week",0)), reverse=True)

st.markdown(f"<span class='count'><b>{len(filtered)}</b> proyectos encontrados</span>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# CARD TEMPLATE (minimalista)
# -----------------------------
def card_html(p):
    cover = resolve_imgur_cover(p)
    title = p.get("title")
    summary = p.get("summary") or ""

    links = p.get("links", {})
    demo   = links.get("demo")
    repo   = links.get("repo")
    video  = links.get("video")
    report = links.get("report")

    btns = []
    if demo:   btns.append(f"<a class='btn' href='{demo}' target='_blank' rel='noopener'>Demo</a>")
    if repo:   btns.append(f"<a class='btn secondary' href='{repo}' target='_blank' rel='noopener'>Repo</a>")
    if video:  btns.append(f"<a class='btn secondary' href='{video}' target='_blank' rel='noopener'>Video</a>")
    if report: btns.append(f"<a class='btn secondary' href='{report}' target='_blank' rel='noopener'>Reporte</a>")
    if not btns: btns.append("<a class='btn secondary' href='#'>Sin enlaces</a>")

    return (f"<div class='card'>"
            f"<img class='cover' src='{cover}' alt='{title}' loading='lazy'/>"
            f"<div class='body'>"
            f"<div class='title'>{title}</div>"
            f"<div class='summary'>{summary}</div>"
            f"<div class='actions'>{''.join(btns)}</div>"
            f"</div></div>")

# -----------------------------
# RENDER GRID
# -----------------------------
def render_grid(items):
    cards = "".join(card_html(p) for p in items)
    st.markdown(minify_html(f"<div class='grid'>{cards}</div>"), unsafe_allow_html=True)

if not filtered:
    st.info("No hay resultados. Cambia los filtros o limpia la búsqueda.")
else:
    render_grid(filtered)

# -----------------------------
# NOTA
# -----------------------------
st.caption("💡 Camilo Seguro ™")
