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
# ESTILOS (grid compacto + cards)
# -----------------------------
st.markdown("""
<style>
:root{
  --bg:#0E1020; --txt:#EDEEFF; --muted:#A7A8B3; --card:#121320;
  --b:#1E2138; --ring:#6a8bff; --chip:#1a1d33; --chip-b:#2a2f4b;
}
html, body, .stApp{background:var(--bg);color:var(--txt);}
.block-container{max-width:1200px;padding-top:1rem;}

/* GRID compacto y responsivo */
.grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:14px;
}

/* CARD */
.card{
  background:var(--card);
  border:1px solid var(--b);
  border-radius:14px;
  overflow:hidden;
  box-shadow:0 10px 18px rgba(0,0,0,.25);
  transition:transform .15s ease,border-color .2s ease, box-shadow .2s ease;
  display:flex; flex-direction:column;
}
.card:hover{
  transform:translateY(-3px);
  border-color:color-mix(in srgb,var(--ring) 60%,transparent);
  box-shadow:0 14px 26px rgba(106,139,255,.22);
}

/* Portada: altura fija para que no crezca gigante si no carga imagen */
.cover{
  width:100%;
  height:140px;             /* <- compacta */
  object-fit:cover;
  background:#0b0d1a;
}

/* Contenido */
.body{ padding:10px 12px 12px; display:flex; flex-direction:column; gap:6px; }
.title{ font-weight:800; margin:0; font-size:.98rem; line-height:1.2; }
.sub{ color:var(--muted); font-size:.8rem; display:flex; gap:6px; flex-wrap:wrap; }
.badge{ padding:.12rem .45rem; border-radius:999px; border:1px solid var(--chip-b); background:var(--chip); font-size:.72rem; color:#dbe0ff; }
.week{ background:#17213a; border-color:#2b3d66; }
.device{ background:#182133; border-color:#2a385b; }

.chips{ display:flex; gap:6px; flex-wrap:wrap; margin-top:2px;}
.chip{ font-size:.72rem; padding:.18rem .45rem; border-radius:999px; border:1px solid var(--chip-b); background:var(--chip); color:#dbe0ff; }

.actions{ display:flex; gap:6px; margin-top:6px; }
.btn{
  display:inline-block; text-decoration:none; text-align:center;
  font-weight:700; font-size:.82rem; color:#fff;
  border:1px solid #2a2f4b; border-radius:9px; padding:.38rem .55rem;
  background:linear-gradient(120deg,#536dff,#8a5bff);
  flex:1 1 auto;
}
.btn.secondary{ background:rgba(255,255,255,.06); color:#cfd6ff; }
.btn:hover{ filter:brightness(1.05); border-color:#3b4163; }

hr{ border:none; border-top:1px solid #1b1e34; margin:.7rem 0 1rem 0; }
.count{ color:var(--muted); }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers (portadas)
# -----------------------------
IMGUR_MAP = {}
IMGUR_PLACEHOLDER = "https://i.imgur.com/U2p7Z3W.jpg"

def resolve_imgur_cover(p: dict) -> str:
    url = (p.get("cover_imgur") or "").strip()
    if url.startswith("https://i.imgur.com/"): return url
    cover_key = (p.get("cover") or "").strip()
    if cover_key in IMGUR_MAP: return IMGUR_MAP[cover_key]
    if cover_key.startswith("https://i.imgur.com/"): return cover_key
    return IMGUR_PLACEHOLDER

# -----------------------------
# DATA
# -----------------------------
def get_projects():
    data = load_projects()
    for p in data:
        p.setdefault("title", "Proyecto sin título")
        p.setdefault("slug", "")
        p.setdefault("year", 0)
        p.setdefault("week", 0)
        p.setdefault("modality", [])
        p.setdefault("device", "")
        p.setdefault("type", "")
        p.setdefault("cover", "")
        p.setdefault("cover_imgur", "")
        p.setdefault("summary", "")
        p.setdefault("links", {})
        p.setdefault("order", 0)
    return data

projects = get_projects()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("# Portafolio — **Interfaces Multimodales**")
st.caption("Universidad EAFIT · Camilo Seguro · 15 entregas")
st.divider()

# -----------------------------
# FILTROS
# -----------------------------
col1, col2, col3, col4 = st.columns([2,1,1,1])
with col1:
    q = st.text_input("Buscar", placeholder="Ej: voz, gestos, Quest, semana 6").strip().lower()
with col2:
    mods = sorted(set(m for p in projects for m in p.get("modality", [])))
    sel_mod = st.selectbox("Modalidad", ["(Todas)"] + mods, index=0)
with col3:
    years = sorted({p.get("year",0) for p in projects if p.get("year")}, reverse=True)
    sel_year = st.selectbox("Año", ["(Todos)"] + [str(y) for y in years], index=0)
with col4:
    group_week = st.toggle("Agrupar por semana", value=False)

def match(p):
    haystack = " ".join([
        p.get("title",""), p.get("summary",""),
        " ".join(p.get("modality",[])), p.get("device",""),
        str(p.get("week","")), str(p.get("year","")), p.get("type",""), p.get("slug","")
    ]).lower()
    if q and not all(tok in haystack for tok in q.split()): return False
    if sel_mod != "(Todas)" and sel_mod not in p.get("modality", []): return False
    if sel_year != "(Todos)" and str(p.get("year",0)) != sel_year: return False
    return True

filtered = [p for p in projects if match(p)]
filtered.sort(key=lambda p: (p.get("year",0), p.get("week",0), p.get("order",0)), reverse=True)

st.markdown(f"<span class='count'><b>{len(filtered)}</b> proyectos encontrados</span>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# Plantilla HTML de tarjeta
# -----------------------------
def card_html(p):
    cover = resolve_imgur_cover(p)
    title = p.get("title")
    week, year = p.get("week"), p.get("year")

    chips = "".join(f"<span class='chip'>{m}</span>" for m in p.get("modality", [])[:3])
    if p.get("device"):
        chips += f"<span class='chip'>🎯 {p.get('device')}</span>"

    meta = f"<span class='badge week'>Semana {week}</span><span class='badge'>{year}</span>"

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
    if not btns:
        btns.append("<a class='btn secondary' href='#'>Sin enlaces</a>")

    return f"""
    <div class="card">
      <img class="cover" src="{cover}" alt="{title}" loading="lazy" referrerpolicy="no-referrer"/>
      <div class="body">
        <div class="title">{title}</div>
        <div class="sub">{meta}</div>
        <div class="chips">{chips}</div>
        <div class="actions">{''.join(btns)}</div>
      </div>
    </div>
    """

# -----------------------------
# RENDER: construir TODO en un solo HTML (clave para que el grid funcione)
# -----------------------------
def render_grid(items):
    cards = [card_html(p) for p in items]
    html = f"<div class='grid'>{''.join(cards)}</div>"
    st.markdown(html, unsafe_allow_html=True)

if not filtered:
    st.info("No hay resultados. Cambia los filtros o limpia la búsqueda.")
else:
    if group_week:
        groups = {}
        for p in filtered:
            groups.setdefault((p.get("year",0), p.get("week",0)), []).append(p)
        for (yy, ww) in sorted(groups.keys(), reverse=True):
            st.markdown(f"### Semana {ww} · {yy}")
            render_grid(groups[(yy, ww)])
            st.markdown("<hr/>", unsafe_allow_html=True)
    else:
        render_grid(filtered)

# -----------------------------
# NOTA
# -----------------------------
st.caption("💡 El grid funciona porque se renderiza en **una sola llamada** a Markdown. La portada usa altura fija (140px) para mantener tarjetas compactas.")
