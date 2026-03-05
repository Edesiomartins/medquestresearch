import json
from typing import Any, Dict, List, Optional

import psycopg2  # type: ignore[reportMissingImports]


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
            # graph_data já deve ser JSON no banco; psycopg2 normalmente
            # retorna como dict se o tipo é json/jsonb, mas garantimos via json.loads se vier string.
            data = row["graph_data"] if isinstance(row, dict) else row[0]
            if isinstance(data, str):
                return json.loads(data)
            return data
        return None
    finally:
        cur.close()


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
        cur.execute(
            """
            SELECT analysis_json
            FROM research_jobs
            WHERE project_id = %s
            """,
            (project_id,),
        )
        rows = cur.fetchall()

        studies: List[Dict[str, Any]] = []
        for idx, row in enumerate(rows):
            analysis_json = row["analysis_json"] if isinstance(row, dict) else row[0]
            if not analysis_json:
                continue
            data = analysis_json
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    continue
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

