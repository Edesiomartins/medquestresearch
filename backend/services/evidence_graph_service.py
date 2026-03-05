import json
import re
import unicodedata
from typing import Any, Dict, List, Optional

import psycopg2  # type: ignore[reportMissingImports]


def _normalize_label_for_id(label: str) -> str:
    """
    Gera um id canônico a partir do label para merge seguro.
    Ex: "Blood pressure" e "blood pressure" e "BP" → normalizados para deduplicação.
    Outcome/Intervention com mesmo label normalizado viram um único nó.
    """
    if not label or not isinstance(label, str):
        return ""
    s = unicodedata.normalize("NFKD", label.lower().strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s).strip("_")
    return s[:80] if s else ""


def build_graph_from_extraction_json(
    extraction_json: Dict[str, Any],
    study_label: Optional[str] = None,
    study_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Constrói um fragmento de graph (nodes + edges) a partir do JSON de extração da Etapa 2.
    Um artigo = um Study + Outcomes + Intervention + edges.

    study_label: título do artigo (ex: "Smith 2021"); se None, usa study_metadata do JSON.
    study_id: id do job (ex: job_id); usado como sufixo estável para o Study node.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    meta = extraction_json.get("study_metadata") or {}
    title_from_meta = (meta.get("title") or meta.get("authors") or "").strip()[:100]
    year = meta.get("year") or ""
    label = study_label or (f"{title_from_meta} {year}".strip() or "Estudo")
    sid = study_id if study_id is not None else 0
    study_id_str = f"study_job_{sid}"
    nodes.append({"id": study_id_str, "type": "Study", "label": label})

    interv_label = "Intervenção"
    interv_canonical = _normalize_label_for_id(interv_label) or "intervencao"
    interv_id = f"intervention_{interv_canonical}_{sid}"
    nodes.append({"id": interv_id, "type": "Intervention", "label": interv_label})
    edges.append({"source": study_id_str, "target": interv_id, "relation": "tests_intervention"})

    n_t_meta = meta.get("intervention_group_n") or 0
    n_c_meta = meta.get("control_group_n") or 0
    if not n_t_meta and not n_c_meta and meta.get("total_sample_size"):
        total = int(meta.get("total_sample_size", 0)) or 0
        if total:
            n_t_meta = total // 2
            n_c_meta = total - n_t_meta

    # Outcome com id canônico + Result com dados numéricos (para detectar_metaanalises_possiveis)
    for i, out in enumerate(extraction_json.get("outcomes") or []):
        if not isinstance(out, dict):
            continue
        name = out.get("outcome_name") or out.get("measure_type") or f"Outcome {i+1}"
        name_str = str(name)[:80]
        canonical = _normalize_label_for_id(name_str) or f"outcome_{i}"
        out_id = f"outcome_{canonical}"
        nodes.append({"id": out_id, "type": "Outcome", "label": name_str})
        edges.append({"source": study_id_str, "target": out_id, "relation": "reports_outcome"})

        intr = out.get("intervention_results") or {}
        ctrl = out.get("control_results") or {}
        n_t = int(out.get("intervention_group_n") or n_t_meta or 0)
        n_c = int(out.get("control_group_n") or n_c_meta or 0)
        if not n_t and (intr.get("sd_or_total") or ctrl.get("sd_or_total")):
            n_t = int(intr.get("sd_or_total") or 0) or n_t_meta
        if not n_c and (intr.get("sd_or_total") or ctrl.get("sd_or_total")):
            n_c = int(ctrl.get("sd_or_total") or 0) or n_c_meta

        # Result node com dados para meta_stats (continuous: mean/sd/n; binary: events/n)
        data: Dict[str, Any] = {"outcome_id": out_id}
        mean_t = intr.get("mean_or_event")
        sd_t = intr.get("sd_or_total")
        mean_c = ctrl.get("mean_or_event")
        sd_c = ctrl.get("sd_or_total")
        if mean_t is not None and mean_c is not None and n_t and n_c:
            try:
                mt, st = float(mean_t), (float(sd_t) if sd_t is not None else 0.0)
                mc, sc = float(mean_c), (float(sd_c) if sd_c is not None else 0.0)
                if st >= 0 and sc >= 0:
                    data.update({"mean_t": mt, "sd_t": st, "n_t": n_t, "mean_c": mc, "sd_c": sc, "n_c": n_c})
            except (TypeError, ValueError):
                pass
        if not data.get("mean_t") and (intr.get("mean_or_event") is not None or ctrl.get("mean_or_event") is not None):
            try:
                et = int(intr.get("mean_or_event") or 0)
                ec = int(ctrl.get("mean_or_event") or 0)
                data.update({"events_t": et, "n_t": n_t or 1, "events_c": ec, "n_c": n_c or 1})
            except (TypeError, ValueError):
                pass
        if len(data) > 1:
            result_id = f"result_{study_id_str}_{canonical}"
            nodes.append({"id": result_id, "type": "Result", "data": data})
            edges.append({"source": study_id_str, "target": result_id, "relation": "has_result"})

    return {"nodes": nodes, "edges": edges}


def merge_graph_safe(existing_graph: Dict[str, Any], new_graph: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge seguro: junta new_graph ao existing_graph.
    - Study: mantém por id único (study_job_X).
    - Outcome/Intervention: deduplicados por id canônico (outcome_blood_pressure, etc.);
      múltiplos estudos podem apontar para o mesmo outcome.
    - Edges: deduplicadas por (source, target, relation).
    """
    nodes_by_id: Dict[str, Dict[str, Any]] = {}
    for g in (existing_graph, new_graph):
        for node in g.get("nodes", []) or []:
            nid = node.get("id")
            if not nid:
                continue
            if nid not in nodes_by_id:
                nodes_by_id[nid] = dict(node)
            elif node.get("type") in ("Outcome", "Intervention"):
                # Mantém primeiro label; pode enriquecer depois
                pass

    edge_set: set = set()
    edges: List[Dict[str, Any]] = []
    for g in (existing_graph, new_graph):
        for edge in g.get("edges", []) or []:
            src = edge.get("source")
            tgt = edge.get("target")
            rel = edge.get("relation") or edge.get("type")
            if not src or not tgt:
                continue
            key = (src, tgt, rel)
            if key in edge_set:
                continue
            edge_set.add(key)
            edges.append({"source": src, "target": tgt, "relation": rel})

    return {"nodes": list(nodes_by_id.values()), "edges": edges}


def salvar_evidence_graph(conn: "psycopg2.extensions.connection", job_id: int, usuario_id: int, graph: Dict[str, Any]) -> int:
    """
    Salva um evidence graph consolidado na tabela evidence_graphs.

    Espera que a tabela evidence_graphs tenha, no mínimo:
      - id (PK, serial/bigserial)
      - research_job_id (int)
      - usuario_id (int)
      - graph_data (json/jsonb)
    """
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO evidence_graphs
            (research_job_id, usuario_id, graph_data)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (job_id, usuario_id, json.dumps(graph)),
        )
        row = cur.fetchone()
        graph_id = row["id"] if isinstance(row, dict) else row[0]
        conn.commit()
        return graph_id
    finally:
        cur.close()


def carregar_evidence_graph(conn: "psycopg2.extensions.connection", job_id: int) -> Optional[Dict[str, Any]]:
    """
    Carrega o evidence graph associado a um research_job_id específico.
    Retorna o dict do graph ou None se não existir.
    """
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT graph_data
            FROM evidence_graphs
            WHERE research_job_id = %s
            """,
            (job_id,),
        )
        row = cur.fetchone()
        if row:
            data = row["graph_data"] if isinstance(row, dict) else row[0]
            if isinstance(data, str):
                return json.loads(data)
            return data
        return None
    finally:
        cur.close()


def carregar_evidence_graph_por_projeto(conn: "psycopg2.extensions.connection", project_id: int) -> Optional[Dict[str, Any]]:
    """
    Carrega o evidence graph do projeto (uma linha por project_id em evidence_graphs).
    Requer coluna project_id em evidence_graphs.
    """
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT graph_data
            FROM evidence_graphs
            WHERE project_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (project_id,),
        )
        row = cur.fetchone()
        if row:
            data = row["graph_data"] if isinstance(row, dict) else row[0]
            if isinstance(data, str):
                return json.loads(data)
            return data
        return None
    finally:
        cur.close()


def upsert_project_evidence_graph(
    conn: "psycopg2.extensions.connection",
    project_id: int,
    usuario_id: int,
    graph: Dict[str, Any],
) -> None:
    """
    Atualiza o Evidence Graph do projeto de forma incremental.
    Carrega o graph existente (se houver), faz merge seguro com o novo graph, salva.
    Requer em evidence_graphs: id, project_id, usuario_id, graph_data (e opcional research_job_id).
    """
    existing = carregar_evidence_graph_por_projeto(conn, project_id)
    if existing and existing.get("nodes"):
        merged = merge_graph_safe(existing, graph)
    else:
        merged = graph

    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id FROM evidence_graphs WHERE project_id = %s LIMIT 1
            """,
            (project_id,),
        )
        row = cur.fetchone()
        graph_json = json.dumps(merged)
        if row:
            eg_id = row["id"] if isinstance(row, dict) else row[0]
            cur.execute(
                "UPDATE evidence_graphs SET graph_data = %s WHERE id = %s",
                (graph_json, eg_id),
            )
        else:
            cur.execute(
                """
                INSERT INTO evidence_graphs (project_id, usuario_id, graph_data)
                VALUES (%s, %s, %s)
                """,
                (project_id, usuario_id, graph_json),
            )
        conn.commit()
    finally:
        cur.close()


def studies_for_outcome(graph: Dict[str, Any], outcome_label: str) -> List[str]:
    """
    Retorna os ids dos Study que reportam o outcome dado.
    Usado na Etapa 5 para saber quais estudos incluir na metanálise para aquele desfecho.
    outcome_label: nome do desfecho (ex: "blood_pressure", "Blood Pressure"); é normalizado para match.
    """
    if not graph or not outcome_label:
        return []
    canonical = _normalize_label_for_id(outcome_label)
    if not canonical:
        return []

    nodes = {n["id"]: n for n in (graph.get("nodes") or [])}
    edges = graph.get("edges") or []
    outcome_ids = [
        nid for nid, n in nodes.items()
        if n.get("type") == "Outcome" and _normalize_label_for_id(n.get("label") or "") == canonical
    ]
    if not outcome_ids:
        return []

    study_ids = set()
    for e in edges:
        if e.get("relation") == "reports_outcome" and e.get("target") in outcome_ids:
            src = e.get("source")
            if src and nodes.get(src, {}).get("type") == "Study":
                study_ids.add(src)
    return list(study_ids)


def extraction_json_to_graph(extraction: Dict[str, Any], study_suffix: str = "") -> Dict[str, Any]:
    """
    Converte o JSON de extração (Etapa 2: PICO + outcomes + dados) em um fragmento de graph
    com nodes (Study, Outcome, Intervention) e edges (reports_outcome, tests_intervention).
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    meta = extraction.get("study_metadata") or {}
    title = (meta.get("title") or meta.get("authors") or "Estudo").strip()[:100]
    year = meta.get("year") or ""
    study_label = f"{title} {year}".strip() or "Estudo"
    base = "".join(c for c in study_label if c.isalnum() or c in " _")[:30].strip() or "s"
    study_id = f"study_{base}_{study_suffix}" if str(study_suffix) else f"study_{base}"

    nodes.append({"id": study_id, "type": "Study", "label": study_label})

    # Nó genérico de intervenção (extração não traz nome da intervenção)
    interv_id = f"intervention_{study_id}"
    nodes.append({"id": interv_id, "type": "Intervention", "label": "Intervenção"})
    edges.append({"source": study_id, "target": interv_id, "relation": "tests_intervention"})

    for i, out in enumerate(extraction.get("outcomes") or []):
        if not isinstance(out, dict):
            continue
        name = out.get("outcome_name") or out.get("measure_type") or f"Outcome {i+1}"
        out_id = f"outcome_{study_id}_{i}"
        nodes.append({"id": out_id, "type": "Outcome", "label": str(name)[:80]})
        edges.append({"source": study_id, "target": out_id, "relation": "reports_outcome"})

    return {"nodes": nodes, "edges": edges}


def merge_graphs(studies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Recebe uma lista de graphs (um por estudo/projeto) e consolida em um único Evidence Graph.

    Cada graph esperado no formato:
    {
      "nodes": [...],
      "edges": [...]
    }

    Nodes são deduplicados por 'id'; edges por (source, target, relation).
    """
    merged_nodes: Dict[str, Dict[str, Any]] = {}
    merged_edges_set = set()
    merged_edges: List[Dict[str, Any]] = []

    for g in studies:
        if not isinstance(g, dict):
            continue

        for node in g.get("nodes", []) or []:
            node_id = node.get("id")
            if not node_id:
                continue
            # Se já existir, mantemos o primeiro; se quiser mesclar propriedades,
            # isso pode ser ajustado depois.
            if node_id not in merged_nodes:
                merged_nodes[node_id] = dict(node)

        for edge in g.get("edges", []) or []:
            source = edge.get("source")
            target = edge.get("target")
            relation = edge.get("relation") or edge.get("type")
            if not source or not target:
                continue
            key = (source, target, relation)
            if key in merged_edges_set:
                continue
            merged_edges_set.add(key)
            merged_edges.append(
                {
                    "source": source,
                    "target": target,
                    "relation": relation,
                }
            )

    return {
        "nodes": list(merged_nodes.values()),
        "edges": merged_edges,
    }


def construir_evidence_graph_para_projeto(
    conn: "psycopg2.extensions.connection",
    project_id: int,
    usuario_id: int,
    job_id: int,
) -> Dict[str, Any]:
    """
    Constrói e persiste um Evidence Graph a partir dos estudos de um projeto.

    Fluxo:
      1) SELECT analysis_json FROM research_jobs WHERE project_id = %s
      2) graph = merge_graphs(studies)
      3) salvar_evidence_graph(conn, job_id, usuario_id, graph)

    Retorna o graph consolidado.
    """
    cur = conn.cursor()
    try:
        # Usa dados_extras (sem coluna analysis_json); extraction_json fica dentro de dados_extras
        cur.execute(
            """
            SELECT dados_extras
            FROM research_jobs
            WHERE project_id = %s AND dados_extras IS NOT NULL
            """,
            (project_id,),
        )
        rows = cur.fetchall()

        studies: List[Dict[str, Any]] = []
        for idx, row in enumerate(rows):
            dados_extras = row["dados_extras"] if isinstance(row, dict) else row[0]
            if not dados_extras:
                continue
            if isinstance(dados_extras, str):
                try:
                    dados_extras = json.loads(dados_extras)
                except Exception:
                    continue
            if not isinstance(dados_extras, dict):
                continue
            # Extração da Etapa 2 fica em dados_extras["extraction_json"]
            data = dados_extras.get("extraction_json") or dados_extras.get("analysis_json") or dados_extras
            if not isinstance(data, dict):
                continue
            # Se já for graph (nodes + edges), usa como está
            if data.get("nodes") is not None and data.get("edges") is not None:
                studies.append(data)
            # Se for JSON de extração (Etapa 2), converte em graph
            elif data.get("study_metadata") or data.get("outcomes"):
                studies.append(extraction_json_to_graph(data, study_suffix=str(idx)))

        graph = merge_graphs(studies)
        salvar_evidence_graph(conn, job_id, usuario_id, graph)
        return graph
    finally:
        cur.close()

