import streamlit as st
from lib.data import load_projects
from itertools import chain
from functools import lru_cache

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Portafolio — Interfaces Multimodales",
    page_icon="🎛️",
    layout="wide",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "Portafolio académico • Interfaces Multimodales • Universidad EAFIT"
    }
)

# -----------------------------
# STYLES
# -----------------------------
st.markdown("""
<style>
:root{
  --bg:#0E1020; --txt:#EDEEFF; --muted:#A7A8B3;
  --card:#121320; --card-b:#1E2138; --ring:#06B6D4; --ring-a:#06B6D477;
  --chip:#1B1D30; --chip-b:#282B46;
  --ok:#22c55e; --warn:#f59e0b; --info:#06b6d4;
}
html, body, .stApp { background: var(--bg); color: var(--txt); }
.block-container{ max-width: 1140px; padding-top: 1.2rem; }

h1, h2, h3 { letter-spacing:.2px }
.stMetric { background: linear-gradient(180deg, #121320, #0f1122); border:1px solid #1b1e34; border-radius:16px; padding:.6rem .8rem }
.stMetric > div { color: var(--muted) !important }
[data-testid="stMetricDelta"] { font-weight:600 }

.grid{ display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:16px }
@media (max-width:1100px){ .grid{ grid-template-columns: repeat(2,1fr); } }
@media (max-width:640px){ .grid{ grid-template-columns: 1fr; } }

.card{
  background: var(--card);
  border: 1px solid var(--card-b);
  border-radius: 20px; overflow: hidden;
  transition: transform .16s ease, border-color .2s ease, box-shadow .2s ease;
  box-shadow: 0 12px 24px rgba(0,0,0,.28);
}
.card:hover{ transform: translateY(-2px); border-color: var(--ring-a); box-shadow: 0 16px 30px rgba(6,182,212,.12); }
.card-cover{ aspect-ratio: 16/9; width:100%; object-fit: cover; background:#0b0d1a }
.card-body{ padding: 14px 14px 16px }
.card-title{ font-weight: 800; margin: 0 0 6px 0; font-size: 1.02rem; letter-spacing:.2px }
.card-sub{ color: var(--muted); font-size: .9rem; margin-bottom: 10px }

.row{ display:flex; gap:8px; align-items:center; flex-wrap: wrap }
.chip{
  display:inline-flex; gap:.45rem; align-items:center;
  padding:.28rem .62rem; border-radius: 999px;
  background: var(--chip); color:#DADEF7; font-size:.78rem;
  border:1px solid var(--chip-b)
}
.chip.badge{ font-weight:700; letter-spacing:.2px; }

.btn{
  display:inline-flex; align-items:center; gap:.5rem;
  padding:.55rem .9rem; border-radius: 999px;
  border:1px solid #2A2A3A; text-decoration:none; color:white;
  font-weight:700; font-size:.9rem
}
.btn:hover{ border-color:#3A3A4F }

.skeleton{
  position: relative; overflow: hidden; background: #14162a;
  border:1px solid #1b1e34; border-radius:20px; aspect-ratio:16/9
}
.skeleton::after{
  content:""; position:absolute; inset:0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.06), transparent);
  transform: translateX(-100%); animation: shimmer 1.3s infinite;
}
@keyframes shimmer{ 100%{ transform: translateX(100%); } }

.small{ font-size:.9rem; color:var(--muted) }
hr{ border:none; border-top:1px solid #1a1d33; margin: .8rem 0 1rem 0 }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
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
        p.setdefault("featured", False)
        p.setdefault("type", "")
    return data

projects_raw = get_projects()

# -----------------------------
# QUERY PARAMS helpers (compat)
# -----------------------------
def _get_qp():
    # Devuelve un dict con listas (como la API de Streamlit)
    try:
        # API nueva
        return {k: list(v) if isinstance(v, list) else [v] for k, v in st.query_params.items()}
    except Exception:
        # API experimental
        return st.experimental_get_query_params()

def _set_qp(**kwargs):
    # Limpia valores vacíos y setea según API disponible
    clean = {k: v for k, v in kwargs.items() if v not in (None, "", [], {}, set())}
    try:
        st.query_params.clear()
        for k, v in clean.items():
            st.query_params[k] = v
    except Exception:
        st.experimental_set_query_params(**clean)

qp = _get_qp()

def get_qp_first(key:str, default:str=""):
    if key not in qp: return default
    val = qp.get(key, [])
    return val[0] if isinstance(val, list) and val else default

# -----------------------------
# HEADER
# -----------------------------
st.markdown("# Portafolio Académico — **Interfaces Multimodales**")
st.caption("Universidad EAFIT · Camilo Seguro · 15 entregas")

# MÉTRICAS (dataset completo)
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Entregas", len(projects_raw))
with col2: st.metric("Modalidades", len(set(chain.from_iterable(p.get("modality", []) for p in projects_raw))))
with col3: st.metric("Dispositivos", len({p.get("device","") for p in projects_raw if p.get("device")}))
with col4: st.metric("Año más reciente", max((p.get("year",0) for p in projects_raw), default=0))

st.divider()

# -----------------------------
# SIDEBAR — FILTROS
# -----------------------------
with st.sidebar:
    st.subheader("Filtrar")
    all_modalities = sorted(set(chain.from_iterable(p.get("modality", []) for p in projects_raw)))
    all_devices = sorted({p.get("device","") for p in projects_raw if p.get("device")})
    all_years = sorted({p.get("year",0) for p in projects_raw if p.get("year")}, reverse=True)

    q_default = get_qp_first("q", "")
    q = st.text_input("Buscar (título, modalidad, semana…)", value=q_default, placeholder="Ej: voz, gestos, Quest, semana 6")

    sel_modal = st.multiselect("Modalidad", options=all_modalities, default=qp.get("mod", []))
    sel_dev = st.multiselect("Dispositivo", options=all_devices, default=qp.get("dev", []))
    sel_year_defaults = [int(y) for y in qp.get("year", [])] if "year" in qp else []
    sel_year = st.multiselect("Año", options=all_years, default=sel_year_defaults)

    st.caption("Ordenar y vista")
    sort_by = st.selectbox("Ordenar por", options=["Más recientes", "A-Z", "Semana", "Año"], index=0)

    # ✅ FIX: usar default_value (no 'default')
    view = st.segmented_control(
        "Vista",
        options=["Cards", "Tabla"],
        default_value=get_qp_first("view", "Cards")
    )

    st.caption("Paginación")
    ps_default = int(get_qp_first("ps", "9"))
    page_size = st.select_slider("Items por página", options=[6, 9, 12, 15, 24], value=ps_default if ps_default in [6,9,12,15,24] else 9)

# -----------------------------
# APLICAR FILTROS
# -----------------------------
def match_query(p, text:str):
    if not text: return True
    t = text.lower().strip()
    haystack = " ".join([
        p.get("title",""),
        " ".join(p.get("modality",[])),
        p.get("device",""),
        str(p.get("week","")),
        str(p.get("year","")),
        p.get("type","")
    ]).lower()
    return all(tok in haystack for tok in t.split())

filtered = []
for p in projects_raw:
    if not match_query(p, q): continue
    if sel_modal and not (set(sel_modal) & set(p.get("modality",[]))): continue
    if sel_dev and p.get("device","") not in sel_dev: continue
    if sel_year and p.get("year",0) not in sel_year: continue
    filtered.append(p)

# Orden
if sort_by == "Más recientes":
    filtered.sort(key=lambda p: (p.get("year",0), p.get("week",0), p.get("title","").lower()), reverse=True)
elif sort_by == "A-Z":
    filtered.sort(key=lambda p: p.get("title","").lower())
elif sort_by == "Semana":
    filtered.sort(key=lambda p: (p.get("week",0), p.get("year",0)))
elif sort_by == "Año":
    filtered.sort(key=lambda p: (p.get("year",0), p.get("week",0)))

# -----------------------------
# TOP/DESTACADOS
# -----------------------------
featured = [p for p in filtered if p.get("featured", False)]
if featured:
    st.subheader("Destacados ✨")
    st.markdown("<div class='grid'>", unsafe_allow_html=True)
    for p in featured[:3]:
        cover = p.get("cover") or "https://picsum.photos/800/450?blur=2"
        mods = ", ".join(p.get("modality", []))
        device = p.get("device","")
        st.markdown(f"""
        <div class="card">
            <img class="card-cover" src="{cover}" alt="{p.get('title')}" />
            <div class="card-body">
                <div class="card-title">{p.get('title')}</div>
                <div class="card-sub">{mods} · Semana {p.get('week')} · {p.get('year')}</div>
                <div class="row" style="margin-bottom:.6rem">
                    {''.join(f'<span class="chip">{m}</span>' for m in p.get('modality',[]))}
                    {f'<span class="chip badge">🎯 {device}</span>' if device else ''}
                </div>
                <a class="btn" href="/?page=Proyectos&slug={p.get('slug')}" target="_self">Ver detalle →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# LISTA PRINCIPAL (Cards / Tabla) con paginación
# -----------------------------
# Persistencia de filtros en URL
_set_qp(
    q=q,
    mod=sel_modal,
    dev=sel_dev,
    year=[str(y) for y in sel_year],
    view=view,
    ps=str(page_size)
)

# Paginación
total = len(filtered)
st.subheader(f"Proyectos ({total})")

if total == 0:
    st.info("No hay resultados con esos filtros. Intenta remover alguno o cambiar la búsqueda.")
else:
    page_str = get_qp_first("page", "1")
    try:
        page = max(1, int(page_str))
    except ValueError:
        page = 1
    max_page = max(1, (total + page_size - 1) // page_size)

    col_a, col_b, col_c = st.columns([1,2,1])
    with col_a:
        if st.button("← Anterior", disabled=(page <= 1)):
            page = max(1, page - 1)
    with col_b:
        st.markdown(f"<div class='small' style='text-align:center'>Página {page} de {max_page}</div>", unsafe_allow_html=True)
    with col_c:
        if st.button("Siguiente →", disabled=(page >= max_page)):
            page = min(max_page, page + 1)

    # Actualiza página en URL
    _set_qp(
        q=q,
        mod=sel_modal,
        dev=sel_dev,
        year=[str(y) for y in sel_year],
        view=view,
        ps=str(page_size),
        page=str(page)
    )

    start = (page - 1) * page_size
    end = start + page_size
    page_items = filtered[start:end]

    if view == "Cards":
        st.markdown("<div class='grid'>", unsafe_allow_html=True)
        for p in page_items:
            cover = p.get("cover") or ""
            if not cover:
                st.markdown("""
                    <div class="card">
                        <div class="skeleton"></div>
                        <div class="card-body">
                            <div class="card-title">Cargando…</div>
                            <div class="card-sub">—</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                mods = ", ".join(p.get("modality", []))
                device = p.get("device","")
                st.markdown(f"""
                <div class="card">
                    <img class="card-cover" src="{cover}" alt="{p.get('title')}" />
                    <div class="card-body">
                        <div class="card-title">{p.get('title')}</div>
                        <div class="card-sub">{mods} · Semana {p.get('week')} · {p.get('year')}</div>
                        <div class="row" style="margin-bottom:.6rem">
                            {''.join(f'<span class="chip">{m}</span>' for m in p.get('modality',[]))}
                            {f'<span class="chip badge">🎯 {device}</span>' if device else ''}
                            {f'<span class="chip">📦 {p.get("type")}</span>' if p.get("type") else ''}
                        </div>
                        <a class="btn" href="/?page=Proyectos&slug={p.get('slug')}" target="_self">Ver detalle →</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        import pandas as pd
        df = pd.DataFrame([{
            "Título": p.get("title"),
            "Modalidad": ", ".join(p.get("modality",[])),
            "Dispositivo": p.get("device",""),
            "Semana": p.get("week"),
            "Año": p.get("year"),
            "Tipo": p.get("type",""),
            "Slug": p.get("slug")
        } for p in page_items])
        st.dataframe(df, use_container_width=True, hide_index=True)

# -----------------------------
# NOTA / CTA
# -----------------------------
st.info("Ve a **Proyectos** para filtrar por modalidad (voz, gestos, hápticos), dispositivo (Quest, móvil, PC), tipo de entrega y semana. También puedes compartir esta vista: la URL guarda tus filtros.")

