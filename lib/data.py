import yaml
from pathlib import Path
from typing import List, Dict, Any
import re

ROOT = Path(__file__).resolve().parent.parent

def load_projects() -> List[Dict[str, Any]]:
    path = ROOT / "projects.yaml"
    with open(path, "r", encoding="utf-8") as f:
        projects = yaml.safe_load(f) or []
    for p in projects:
        p["slug"] = slugify(p.get("slug") or p.get("title",""))
        p["tags"] = [str(t) for t in (p.get("tags") or [])]
        try: p["year"] = int(p.get("year") or 0)
        except: p["year"] = 0
    return projects

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9áéíóúñü\-\s]", "", text)
    text = text.replace(" ", "-")
    return text

def search(projects, q: str):
    if not q: return projects
    ql = q.lower()
    def hit(p):
        hay = " ".join([
            p.get("title",""),
            p.get("summary",""),
            " ".join(p.get("tags",[])),
            " ".join(p.get("tools",[])),
            p.get("role",""),
            p.get("course",""),
            p.get("instructor",""),
            p.get("deliverable",""),
            " ".join(p.get("modality",[])),
            " ".join(p.get("input_types",[])),
            " ".join(p.get("output_types",[])),
            p.get("device",""),
        ]).lower()
        return all(tok in hay for tok in ql.split())
    return [p for p in projects if hit(p)]