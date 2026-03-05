# Detecta grupos de estudos compatíveis para metanálise a partir do Evidence Graph.
# Agrupa por Outcome; dentro de cada outcome, separa por tipo (continuous vs binary) e por intervenção/comparador.
# Requer grafo com nodes tipo Study, Outcome e (opcional) Result, e edges reports_outcome e has_result.

from collections import defaultdict
from typing import Any, Dict, List


def _tipo_outcome(node: Dict[str, Any]) -> str:
    """Define tipo do outcome a partir dos campos disponíveis (em node ou node['data'])."""
    data = node.get("data", node) if isinstance(node.get("data"), dict) else (node.get("data") or {})
    if not isinstance(data, dict):
        data = {}
    if all(k in data for k in ("mean_t", "sd_t", "n_t", "mean_c", "sd_c", "n_c")):
        return "continuous"
    if all(k in data for k in ("events_t", "n_t", "events_c", "n_c")):
        return "binary"
    return "unknown"


def _key_interv_comp(node: Dict[str, Any]) -> str:
    """Cria chave simples intervenção vs comparador (se existir)."""
    data = node.get("data", node) if isinstance(node.get("data"), dict) else (node.get("data") or {})
    if not isinstance(data, dict):
        data = {}
    interv = (data.get("intervention") or "").strip().lower()
    comp = (data.get("comparator") or "").strip().lower()
    return f"{interv}__vs__{comp}" if interv or comp else "unknown"


def detectar_metaanalises_possiveis(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recebe evidence_graph (dict com nodes/edges) e retorna grupos de estudos compatíveis para metanálise.

    Espera no grafo:
    - nodes com type: Study, Outcome, Result (Result com data: mean_t, sd_t, n_t, etc. ou events_t/n_t/events_c/n_c)
    - edges: reports_outcome (Study -> Outcome), has_result (Study -> Result)

    Se o grafo não tiver Result nodes / has_result, retorna lista vazia (grafo pode ser enriquecido depois).
    """
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []

    outcomes = {n["id"]: n for n in nodes if n.get("type") == "Outcome"}
    studies = {n["id"]: n for n in nodes if n.get("type") == "Study"}
    results = {n["id"]: n for n in nodes if n.get("type") == "Result"}

    outcome_to_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    result_to_outcome: Dict[str, str] = {}
    for e in edges:
        if e.get("relation") == "for_outcome" and e.get("source") in results and e.get("target") in outcomes:
            result_to_outcome[e["source"]] = e["target"]

    for e in edges:
        if e.get("relation") == "reports_outcome":
            study_id = e.get("source")
            outcome_id = e.get("target")
            if not study_id or not outcome_id:
                continue
            for e2 in edges:
                if (
                    e2.get("relation") == "has_result"
                    and e2.get("source") == study_id
                    and e2.get("target") in results
                ):
                    result_node = results[e2["target"]]
                    rid = e2.get("target")
                    # Só associa ao outcome se result tiver outcome_id no data ou edge for_outcome
                    res_outcome = result_node.get("data", {}).get("outcome_id") or result_to_outcome.get(rid)
                    if res_outcome and res_outcome != outcome_id:
                        continue
                    outcome_to_results[outcome_id].append({
                        "study_id": study_id,
                        "result_node": result_node,
                    })

    candidatos: List[Dict[str, Any]] = []

    for outcome_id, itens in outcome_to_results.items():
        outcome = outcomes.get(outcome_id)
        if not outcome:
            continue

        grupos: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)

        for item in itens:
            result_node = item["result_node"]
            tipo = _tipo_outcome(result_node)
            interv_key = _key_interv_comp(result_node)
            chave = (tipo, interv_key)
            grupos[chave].append(item)

        for (tipo, interv_key), lista in grupos.items():
            if tipo == "unknown":
                continue
            if len(lista) < 2:
                continue
            # Incluir dados numéricos de cada result_node para rodar meta_stats sem lookup externo
            items = [
                {"study_id": i["study_id"], "data": i["result_node"].get("data", {})}
                for i in lista
            ]
            candidatos.append({
                "outcome_id": outcome_id,
                "outcome_label": outcome.get("label"),
                "tipo": tipo,
                "intervention_key": interv_key,
                "n_estudos": len(lista),
                "studies": [i["study_id"] for i in lista],
                "items": items,
            })

    return candidatos
