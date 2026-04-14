from __future__ import annotations

import os
import tempfile
import time
from typing import List

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.schemas.article import ArticleSectionResponse
from backend.schemas.meta import (
    MetaAnalysisResponse,
    MetaAnalyzeRequest,
    MetaReviewRequest,
    MetaUploadResponse,
    MetaPipelineStatus,
)
from backend.services.article_generation_service import generate_article_sections
from backend.services.docx_export_service import build_meta_docx
from backend.services.export_bundle_service import build_submission_zip
from backend.services.extraction_service import extract_studies_from_texts
from backend.services.meta_pipeline_service import analyze_meta
from backend.services.review_validation_service import validate_reviewed_studies

try:
    from backend.database import db_select_one
except Exception:
    from database import db_select_one  # type: ignore

try:
    from backend.pdf_processor import extrair_texto_pdf
except Exception:
    from pdf_processor import extrair_texto_pdf  # type: ignore


router = APIRouter(prefix="/api/meta", tags=["meta-analysis-v2"])


def require_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")
    token = authorization.replace("Bearer ", "").strip()
    user = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not user:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return dict(user)


@router.post("/upload", response_model=MetaUploadResponse)
async def upload_studies(files: List[UploadFile] = File(...), user=Depends(require_api_key)):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")
    if len(files) > 25:
        raise HTTPException(status_code=400, detail="Máximo de 25 arquivos por upload.")

    texts: List[str] = []
    for file in files:
        if not file.filename or not file.filename.lower().endswith((".pdf", ".docx")):
            raise HTTPException(status_code=400, detail=f"Formato não suportado: {file.filename}")
        payload = await file.read()
        if len(payload) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo {file.filename} excede 20MB.",
            )
        temp_name = os.path.join(
            tempfile.gettempdir(),
            f"meta_upload_{time.time_ns()}_{file.filename}",
        )
        with open(temp_name, "wb") as stream:
            stream.write(payload)
        try:
            if file.filename.lower().endswith(".pdf"):
                text = extrair_texto_pdf(temp_name)
                if isinstance(text, list):
                    text = "\n".join(text)
                texts.append(text or "")
            else:
                texts.append(payload.decode("utf-8", errors="ignore"))
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    project_id = str(int(time.time()))
    studies = extract_studies_from_texts(project_id=project_id, texts=texts)
    return MetaUploadResponse(
        status=MetaPipelineStatus.success,
        project_id=project_id,
        studies=studies,
        notes=[f"Usuário {user.get('id')} enviou {len(files)} arquivos."],
    )


@router.post("/extract", response_model=MetaUploadResponse)
def extract_structured(payload: MetaReviewRequest, user=Depends(require_api_key)):
    _ = user
    project_id = payload.project_id or str(int(time.time()))
    return MetaUploadResponse(
        status=MetaPipelineStatus.success,
        project_id=project_id,
        studies=payload.studies,
        notes=["Extração estruturada pronta para revisão humana."],
    )


@router.post("/review", response_model=MetaUploadResponse)
def review_extraction(payload: MetaReviewRequest, user=Depends(require_api_key)):
    _ = user
    project_id = payload.project_id or str(int(time.time()))
    reviewed, notes = validate_reviewed_studies(payload.studies)
    return MetaUploadResponse(
        status=MetaPipelineStatus.success,
        project_id=project_id,
        studies=reviewed,
        notes=notes,
    )


@router.post("/analyze", response_model=MetaAnalysisResponse)
def analyze(payload: MetaAnalyzeRequest, user=Depends(require_api_key)):
    _ = user
    if len(payload.question or "") > 1000:
        raise HTTPException(status_code=400, detail="Pergunta de pesquisa muito longa (máx. 1000 caracteres).")
    return analyze_meta(payload)


@router.post("/plots", response_model=dict)
def plots(payload: MetaAnalyzeRequest, user=Depends(require_api_key)):
    _ = user
    result = analyze_meta(payload)
    return {
        "status": result.status,
        "project_id": result.project_id,
        "forest_plot_svg": result.forest_plot_svg,
        "funnel_plot_svg": result.funnel_plot_svg,
    }


@router.post("/article", response_model=ArticleSectionResponse)
def article(payload: MetaAnalyzeRequest, section: str = "results", user=Depends(require_api_key)):
    _ = user
    result = analyze_meta(payload)
    sections = generate_article_sections(result.dict())
    content = getattr(sections, section, None)
    if not content:
        raise HTTPException(status_code=400, detail=f"Seção inválida: {section}")
    return ArticleSectionResponse(
        section=section,
        content=content,
        warnings=result.warnings,
    )


@router.post("/export/docx")
def export_docx(
    payload: MetaAnalyzeRequest,
    filename: str = "meta_analise",
    user=Depends(require_api_key),
):
    _ = user
    result = analyze_meta(payload)
    docx_bytes = build_meta_docx(result.dict())
    safe_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in filename).strip("_") or "meta_analise"
    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}.docx"'
    }
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.post("/export/zip")
def export_zip(
    payload: MetaAnalyzeRequest,
    filename: str = "meta_analise_submission",
    user=Depends(require_api_key),
):
    _ = user
    result = analyze_meta(payload)
    zip_bytes = build_submission_zip(result.dict())
    safe_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in filename).strip("_") or "meta_analise_submission"
    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}.zip"'
    }
    return StreamingResponse(
        iter([zip_bytes]),
        media_type="application/zip",
        headers=headers,
    )

