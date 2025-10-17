import streamlit as st
from lib.data import load_projects
from functools import lru_cache
from itertools import chain

# -----------------------------
# Config básica
# -----------------------------
st.set_page_config(page_title="Portafolio — Interfaces Multimodales", page_icon="🎛️", layout="wide")

# -----------------------------
# Estilos mínimos (dark + cards)
# -----------------------------
st.markdown("""
<style>
:root{ --bg:#0E1020; --txt:#EDEEFF; --muted:#A7A8B3; --card:#121320; --b:#1E2138; --ring:#06B6D4;}
html, body, .stApp{ background:var(--bg); color:var(--txt); }
.block-container{ max-width:1100px; padding-top:1rem; }

.grid{ display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:16px }
@media (max-width:1000px){ .grid{ grid-template-columns:repeat(2,1fr) } }
@media (max-width:640px){ .grid{ grid-template-columns:1fr } }

.card{ background:var(--card); border:1px solid var(--b); border-radius:16px; overflow:hidden;
       box-shadow:0 10px 20px rgba(0,0,0,.25); transition:transform .15s ease, border-color .2s ease }
.card:hover{ transform:translateY(-2px); border-color:color-mix(in srgb, var(--ring) 50%, transparent) }
.cover{ aspect-ratio:16/9; width:100%; object-fit:cover; background:#0b0d1a; display:block }
.body{ padding:12px 12px 14px }
.title{ font-weight:800; margin:0 0 6px 0; font-size:1rem }
.sub{ color:var(--muted); font-size:.9rem; margin-bottom:8px }
.chips{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px }
.chip{ font-size:.75rem; padding:.22rem .5rem; border-radius:999px; border:1px solid #2a2f4b; background:#1a1d33; color:#dae0ff }
.btn{ display:inline-block; font-weight:700; font-size:.9rem; color:white; border:1px solid #2a2f4b; border-radius:999px; padding:.45rem .75rem; text-decoration:none }
.btn:hover{ border-color:#3b4163 }
hr{ border:none; border-top:1px solid #1b1e34; margin: .8rem 0 1rem 0 }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
PLACEHOLDER = "https://picsum.photos/800/450?blur=2"

def resolve_cover(raw: str) -> str:
    if not raw: return PLACEHOLDER
    raw = raw.strip()
    if "://" not in raw:
        return f"/static/{raw.lstrip('/')}"  # usa /static si pones tus imágenes ahí
    if raw.startswith("http://"):
        raw = "https://" + raw[len("http://"):]
    if "github.com" in raw and "/blob/" in raw:
        try:
            parts = raw.split("github.com/")[1]
            user_repo, rest = parts.split("/blob/", 1)
            user, repo = user_repo.split("/", 1)
            branch, path = rest.split("/", 1)
            raw = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
        except Exception:
            pass
    if "dropbox.com" in raw and "dl=0" in raw:
        raw = raw.replace("dl=0", "raw=1")
    return raw

@lru_cache(maxsize=1)
def get_projects():
    data = load_projects()
    for p in data:
        p.setdefault("title", "Proyecto")
        p.setdefault("slug", "")
        p.setdefault("year", 0)
        p.setdefault("week", 0)
        p.setdefault("modality", [])
        p.setdefault("device", "")
        p.setdefault("cover", "")
        p.setdefault("type", "")
    return data

# -----------------------------
# Data
# -----------------------------
projects = get_projects()

# -----------------------------
# Header
# -----------------------------
st.markdown("# Portafolio — **Interfaces Multimodales**")
st.caption("Universidad EAFIT · Camilo Seguro · 15 entregas")
st.divider()

# -----------------------------
# Filtros súper simples
# -----------------------------
colf1, colf2, colf3, colf4 = st.columns([2,1,1,1])
with colf1:
    q = st.text_input("Buscar (título, modalidad, dispositivo, semana…)", placeholder="Ej: voz, gestos, Quest, semana 6").strip().lower()
with colf2:
    mods = sorted(set(chain.from_iterable(p.get("modality", []) for p in projects)))
    sel_mod = st.selectbox("Modalidad", options=["(Todas)"] + mods, index=0)
with colf3:
    devices = sorted({p.get("device","") for p in projects if p.get("device")})
    sel_dev = st.selectbox("Dispositivo", options=["(Todos)"] + devices, index=0)
with colf4:
    years = sorted({p.get("year",0) for p in projects if p.get("year")}, reverse=True)
    sel_year = st.selectbox("Año", options=["(Todos)"] + [str(y) for y in years], index=0)

# -----------------------------
# Filtrado
# -----------------------------
def match(p):
    text = " ".join([
        p.get("title",""),
        " ".join(p.get("modality",[])),
        p.get("device",""),
        str(p.get("week","")),
        str(p.get("year","")),
        p.get("type",""),
    ]).lower()
    if q and not all(tok in text for tok in q.split()): 
        return False
    if sel_mod != "(Todas)" and sel_mod not in p.get("modality", []):
        return False
    if sel_dev != "(Todos)" and p.get("device","") != sel_dev:
        return False
    if sel_year != "(Todos)" and str(p.get("year",0)) != sel_year:
        return False
    return True

filtered = [p for p in projects if match(p)]
filtered.sort(key=lambda p: (p.get("year",0), p.get("week",0), p.get("title","").lower()), reverse=True)

st.markdown(f"**{len(filtered)}** proyectos encontrados")
st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# Grid de imágenes + info
# -----------------------------
if not filtered:
    st.info("No hay resultados. Cambia los filtros o limpia la búsqueda.")
else:
    st.markdown("<div class='grid'>", unsafe_allow_html=True)
    for p in filtered:
        cover = resolve_cover(p.get("cover") or "")
        title = p.get("title")
        sub = f"{', '.join(p.get('modality', []))} · Semana {p.get('week')} · {p.get('year')}"
        chips = ""
        for m in p.get("modality", []):
            chips += f"<span class='chip'>{m}</span>"
        if p.get("device"): chips += f"<span class='chip'>🎯 {p.get('device')}</span>"
        if p.get("type"): chips += f"<span class='chip'>📦 {p.get('type')}</span>"
        detail_url = f"/?page=Proyectos&slug={p.get('slug')}" if p.get("slug") else "#"
        st.markdown(f"""
        <div class="card">
          <img class="cover" src="{cover}" alt="{title}" loading="lazy" referrerpolicy="no-referrer" />
          <div class="body">
            <div class="title">{title}</div>
            <div class="sub">{sub}</div>
            <div class="chips">{chips}</div>
            <a class="btn" href="{detail_url}" target="_self">Ver detalle →</a>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Nota
# -----------------------------
st.caption("Tip: para que las imágenes siempre carguen, usa URLs **https**, enlaces **raw** de GitHub o ponlas en **/static/assets/** y referencia `assets/mi_portada.jpg`.")
