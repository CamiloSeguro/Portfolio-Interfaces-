import streamlit as st
from lib.data import load_projects, search

st.set_page_config(page_title="Proyectos (Interfaces Multimodales)", page_icon="🧩", layout="wide")
st.markdown("<style>\n:root{--card-bg:#121320;--chip-bg:#1B1D30;--chip-txt:#EDEEFF;--muted:#A7A8B3;--ring:#06B6D477;}\n.block-container{max-width:1140px}\n.card{background:var(--card-bg);border:1px solid #1E2138;border-radius:20px;overflow:hidden;\n  transition:transform .15s ease,border-color .2s ease;box-shadow:0 10px 20px rgba(0,0,0,.25)}\n.card:hover{transform:translateY(-2px);border-color:var(--ring)}\n.card-cover{aspect-ratio:16/9;width:100%;object-fit:cover}\n.card-body{padding:14px 14px 16px}\n.card-title{font-weight:700;margin:0 0 6px 0}\n.card-sub{color:var(--muted);font-size:.9rem;margin-bottom:8px}\n.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}\n@media (max-width:1000px){.grid{grid-template-columns:repeat(2,1fr)}}\n@media (max-width:640px){.grid{grid-template-columns:1fr}}\n.chip{display:inline-flex;gap:.4rem;padding:.26rem .6rem;border-radius:999px;background:var(--chip-bg);\n  color:var(--chip-txt);font-size:.78rem;border:1px solid #282B46}\n.btn{display:inline-flex;align-items:center;gap:.5rem;padding:.55rem .9rem;border-radius:999px;\n  border:1px solid #2A2A3A;text-decoration:none;color:white;font-weight:600;font-size:.9rem}\n.btn:hover{border-color:#3A3A4F}\n</style>", unsafe_allow_html=True)

projects = load_projects()

qp = st.query_params
slug = qp.get("slug", [None]) if hasattr(qp, "get") else None
slug = slug[0] if isinstance(slug, list) else slug

with st.sidebar:
    st.header("Filtros")
    mod_pool = sorted({m for p in projects for m in p.get("modality",[])})
    sel_mod = st.multiselect("Modalidad", mod_pool, placeholder="Todas")
    dev_pool = sorted({p.get("device") for p in projects if p.get("device")})
    sel_dev = st.multiselect("Dispositivo", dev_pool, placeholder="Todos")
    weeks = sorted({p.get("week") for p in projects if p.get("week")}, key=lambda x: int(x))
    sel_weeks = st.multiselect("Semana", weeks, placeholder="Todas")
    types = sorted({p.get("deliverable") for p in projects if p.get("deliverable")})
    sel_types = st.multiselect("Tipo de entrega", types, placeholder="Todas")
    q = st.text_input("Buscar", placeholder="tema, herramientas, inputs/outputs...")
    st.page_link("app.py", label="🏠 Home", icon="🏠")

def apply_filters(items):
    out = items
    if sel_mod:
        out = [p for p in out if any(m in p.get("modality",[]) for m in sel_mod)]
    if sel_dev:
        out = [p for p in out if p.get("device") in sel_dev]
    if sel_weeks:
        out = [p for p in out if str(p.get("week")) in [str(w) for w in sel_weeks]]
    if sel_types:
        out = [p for p in out if p.get("deliverable") in sel_types]
    if q:
        out = search(out, q)
    return out

if slug:
    project = next((p for p in projects if p["slug"]==slug), None)
    if not project:
        st.error("Entrega no encontrada."); st.stop()
    col1, col2 = st.columns([1.6,1])
    with col1:
        st.markdown(f"### {project['title']}")
        st.image(project.get("cover"), use_container_width=True)
    with col2:
        st.markdown(f"**Modalidad:** {', '.join(project.get('modality',[]))}")
        st.markdown(f"**Inputs:** {', '.join(project.get('input_types',[]))}")
        st.markdown(f"**Outputs:** {', '.join(project.get('output_types',[]))}")
        st.markdown(f"**Dispositivo:** {project.get('device','')}")
        st.markdown(f"**Semana:** {project.get('week','')} · **Tipo:** {project.get('deliverable','')} · **Año:** {project.get('year','')}")
        if project.get("metrics"):
            st.markdown("**Metricas:** " + ", ".join(project["metrics"]))
        if project.get("tools"):
            st.markdown("**Herramientas:** " + ", ".join(project["tools"]))
        links = project.get("links") or {}
        st.markdown("---")
        for k, lab in [("repo","Repo"),("report","Informe"),("video","Video"),("demo","Demo")]:
            url = links.get(k)
            if url: st.link_button(lab, url)
    st.markdown("#### Resumen")
    st.write(project.get("summary",""))
    if project.get("objectives"):
        st.markdown("#### Objetivos")
        for h in project["objectives"]:
            st.markdown(f"- {h}")
    if project.get("results"):
        st.markdown("#### Resultados")
        for h in project["results"]:
            st.markdown(f"- {h}")
    st.page_link("pages/2_🧩_Proyectos.py", label="← Volver al listado", icon="↩️"); st.stop()

st.markdown("# Proyectos — Interfaces Multimodales")
filtered = apply_filters(projects)
st.caption(f"Mostrando {len(filtered)} de {len(projects)} entregas")
st.markdown("<div class='grid'>", unsafe_allow_html=True)
for p in filtered:
    sub = f"{', '.join(p.get('modality',[]))} · Semana {p.get('week')} · {p.get('year')}"
    href = f"/?page=Proyectos&slug={p['slug']}"
    st.markdown(f'''
    <div class="card">
      <img class="card-cover" src="{p.get('cover','')}" />
      <div class="card-body">
         <div class="card-title">{p.get('title')}</div>
         <div class="card-sub">{sub}</div>
         <a class="btn" href="{href}" target="_self">Ver detalle →</a>
      </div>
    </div>
    ''', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)