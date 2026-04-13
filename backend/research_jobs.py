import json
import logging
import traceback
from typing import Any, Optional

try:
    from .database import get_connection
except ImportError:
    try:
        from database import get_connection
    except ImportError:
        from backend.database import get_connection  # type: ignore[reportMissingImports]

try:
    from .critical_analysis import aplicar_leitura_critica
except ImportError:
    try:
        from critical_analysis import aplicar_leitura_critica
    except ImportError:
        from backend.critical_analysis import aplicar_leitura_critica  # type: ignore[reportMissingImports]

try:
    from .meta_analysis import gerar_meta_analise
except ImportError:
    try:
        from meta_analysis import gerar_meta_analise
    except ImportError:
        from backend.meta_analysis import gerar_meta_analise  # type: ignore[reportMissingImports]

try:
    from .services.evidence_graph_service import (
        build_graph_from_extraction_json,
        upsert_project_evidence_graph,
    )
except ImportError:
    try:
        from services.evidence_graph_service import (
            build_graph_from_extraction_json,
            upsert_project_evidence_graph,
        )
    except ImportError:
        from backend.services.evidence_graph_service import (  # type: ignore[reportMissingImports]
            build_graph_from_extraction_json,
            upsert_project_evidence_graph,
        )


def log_t(msg: str) -> None:
    logging.warning(f"[TIMER] {msg}")


def _update_job_success(job_id: int, resultado: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                ("done", resultado, job_id),
            )
            rowcount = cursor.rowcount
        conn.commit()
        logging.warning(
            f"[RESEARCH JOB {job_id}] UPDATE concluido - job_id={job_id}, linhas_afetadas={rowcount}"
        )
    finally:
        conn.close()


def _update_job_failure(job_id: int, erro: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                ("failed", erro[:1000], job_id),
            )
            rowcount = cursor.rowcount
        conn.commit()
        logging.error(
            f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}"
        )
    finally:
        conn.close()


def run_with_two_chunks(
    texto: str,
    process_func,
    chunk_size: int = 1800,
    overlap: int = 300,
    max_chunks: int = 2,
) -> str:
    try:
        from .chunker import chunk_text, combine_responses
    except ImportError:
        try:
            from chunker import chunk_text, combine_responses
        except ImportError:
            from backend.chunker import chunk_text, combine_responses  # type: ignore[reportMissingImports]

    log_t("ANTES chunking")
    chunks = chunk_text(texto, chunk_size=chunk_size, overlap=overlap)
    log_t("DEPOIS chunking")
    chunks = chunks[:max_chunks]

    respostas = []
    for index, chunk in enumerate(chunks, 1):
        log_t(f"ANTES OpenAI chunk {index}")
        resposta = process_func(chunk)
        log_t(f"DEPOIS OpenAI chunk {index}")
        respostas.append(resposta)

    log_t("ANTES montagem resposta")
    texto_final = combine_responses(respostas)
    log_t("DEPOIS montagem resposta")

    aviso = (
        "\n\nNota: esta analise foi gerada a partir de uma parte do texto "
        "para garantir rapidez e estabilidade da plataforma."
    )
    return texto_final + aviso


def processar_job_critica(job_id: int, texto_artigo: str, foco_analise: str = "geral") -> None:
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] inicio - critica (foco: {foco_analise})")
        resultado = aplicar_leitura_critica(texto_artigo[:3000], foco_analise)
        _update_job_success(job_id, resultado)
        logging.warning(f"[RESEARCH JOB {job_id}] concluido - critica")
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - critica\n{erro}")
        _update_job_failure(job_id, erro)


def _extrair_json_do_texto(texto: str) -> Optional[dict[str, Any]]:
    if not texto or not texto.strip():
        return None

    texto = texto.strip()
    for marker in ("```json", "```"):
        inicio = texto.find(marker)
        if inicio >= 0:
            fim = texto.find("```", inicio + len(marker))
            if fim > inicio:
                bloco = texto[inicio + len(marker):fim].strip()
                try:
                    return json.loads(bloco)
                except Exception:
                    pass

    inicio = texto.find("{")
    if inicio >= 0:
        fim = texto.rfind("}")
        if fim > inicio:
            try:
                return json.loads(texto[inicio:fim + 1])
            except Exception:
                pass
    return None


def processar_job_meta_analise(
    job_id: int,
    tema: str,
    etapa: str = "1",
    texto_artigo: Optional[str] = None,
    dados_extras: Optional[dict[str, Any]] = None,
) -> None:
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] inicio - meta_analise (etapa: {etapa}, tema: {tema})")

        if texto_artigo:
            texto_artigo = texto_artigo[:6000]

        resultado_dict = gerar_meta_analise(
            tema=tema,
            etapa=etapa,
            texto_artigo=texto_artigo,
            dados_extras=dados_extras,
        )

        resultado_texto = resultado_dict.get("resultado", "")
        artigos_encontrados = resultado_dict.get("artigos", [])
        total_artigos = resultado_dict.get("total_artigos", 0)

        dados_extras_atualizados = dados_extras.copy() if dados_extras else {}
        if artigos_encontrados:
            dados_extras_atualizados["artigos"] = artigos_encontrados
            dados_extras_atualizados["total_artigos"] = total_artigos

        parsed = None
        if etapa == "2" and resultado_texto:
            parsed = _extrair_json_do_texto(resultado_texto)
            if isinstance(parsed, dict) and (parsed.get("study_metadata") or parsed.get("outcomes")):
                dados_extras_atualizados["extraction_json"] = parsed

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                dados_extras_json = json.dumps(dados_extras_atualizados) if dados_extras_atualizados else None
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s, dados_extras=%s WHERE id=%s",
                    ("done", resultado_texto, dados_extras_json, job_id),
                )
                rowcount = cursor.rowcount
            conn.commit()
            logging.warning(
                f"[RESEARCH JOB {job_id}] UPDATE concluido - job_id={job_id}, linhas_afetadas={rowcount}, artigos={len(artigos_encontrados)}"
            )

            if (
                etapa == "2"
                and parsed
                and (dados_extras or {}).get("project_id") is not None
                and (dados_extras or {}).get("usuario_id") is not None
            ):
                try:
                    project_id = int((dados_extras or {})["project_id"])
                    usuario_id = int((dados_extras or {})["usuario_id"])
                    meta = parsed.get("study_metadata") or {}
                    titulo_artigo = (meta.get("title") or meta.get("authors") or f"Estudo {job_id}").strip()[:100]
                    year = meta.get("year") or ""
                    study_label = f"{titulo_artigo} {year}".strip() or f"Estudo {job_id}"
                    graph = build_graph_from_extraction_json(parsed, study_label=study_label, study_id=job_id)
                    upsert_project_evidence_graph(conn, project_id, usuario_id, graph)
                    logging.warning(f"[RESEARCH JOB {job_id}] Evidence Graph atualizado (project_id={project_id})")
                except Exception as graph_error:
                    logging.warning(f"[RESEARCH JOB {job_id}] Evidence Graph (nao bloqueante): {graph_error}")
        finally:
            conn.close()

        logging.warning(f"[RESEARCH JOB {job_id}] concluido - meta_analise")
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - meta_analise\n{erro}")
        _update_job_failure(job_id, erro)
