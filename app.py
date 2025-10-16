import streamlit as st
from lib.data import load_projects

st.set_page_config(page_title="Portafolio — Interfaces Multimodales", page_icon="🎛️", layout="wide")
st.markdown("<style>\n:root{--card-bg:#121320;--chip-bg:#1B1D30;--chip-txt:#EDEEFF;--muted:#A7A8B3;--ring:#06B6D477;}\n.block-container{max-width:1140px}\n.card{background:var(--card-bg);border:1px solid #1E2138;border-radius:20px;overflow:hidden;\n  transition:transform .15s ease,border-color .2s ease;box-shadow:0 10px 20px rgba(0,0,0,.25)}\n.card:hover{transform:translateY(-2px);border-color:var(--ring)}\n.card-cover{aspect-ratio:16/9;width:100%;object-fit:cover}\n.card-body{padding:14px 14px 16px}\n.card-title{font-weight:700;margin:0 0 6px 0}\n.card-sub{color:var(--muted);font-size:.9rem;margin-bottom:8px}\n.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}\n@media (max-width:1000px){.grid{grid-template-columns:repeat(2,1fr)}}\n@media (max-width:640px){.grid{grid-template-columns:1fr}}\n.chip{display:inline-flex;gap:.4rem;padding:.26rem .6rem;border-radius:999px;background:var(--chip-bg);\n  color:var(--chip-txt);font-size:.78rem;border:1px solid #282B46}\n.btn{display:inline-flex;align-items:center;gap:.5rem;padding:.55rem .9rem;border-radius:999px;\n  border:1px solid #2A2A3A;text-decoration:none;color:white;font-weight:600;font-size:.9rem}\n.btn:hover{border-color:#3A3A4F}\n</style>", unsafe_allow_html=True)

projects = load_projects()
projects = sorted(projects, key=lambda p: (p.get("year",0), p.get("week",0)))

st.markdown("# Portafolio Academico — **Interfaces Multimodales**")
st.caption("Universidad EAFIT · Camilo Seguro (15 entregas)")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Entregas", len(projects))
with col2: st.metric("Modalidades", len(set(m for p in projects for m in p.get("modality",[]))))
with col3: st.metric("Dispositivos", len(set(p.get("device","") for p in projects if p.get("device"))))
with col4: st.metric("Año", max((p.get("year",0) for p in projects), default=0))

st.divider()
st.subheader("Destacados")
st.markdown("<div class='grid'>", unsafe_allow_html=True)
for p in projects[:6]:
    st.markdown(f'''
    <div class="card">
      <img class="card-cover" src="{p.get('cover','')}" />
      <div class="card-body">
         <div class="card-title">{p.get('title')}</div>
         <div class="card-sub">{", ".join(p.get("modality",[]))} · Semana {p.get('week')} · {p.get('year')}</div>
         <a class="btn" href="/?page=Proyectos&slug={p.get('slug')}" target="_self">Ver detalle →</a>
      </div>
    </div>
    ''', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.info("Ve a **Proyectos** para filtrar por modalidad (voz, gestos, haptics), dispositivo (Quest, movil, PC), tipo de entrega y semana.")
