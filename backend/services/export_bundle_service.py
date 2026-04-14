from __future__ import annotations

import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from backend.services.docx_export_service import build_meta_docx


def _effects_to_csv(meta_result: dict) -> bytes:
    rows = meta_result.get("effects_table") or []
    headers = [
        "study_id",
        "citation",
        "effect_measure",
        "effect",
        "variance",
        "standard_error",
        "ci_low",
        "ci_high",
        "weight_fixed",
        "weight_random",
        "subgroup",
    ]
    lines = [",".join(headers)]
    for row in rows:
        values = []
        for header in headers:
            value = row.get(header, "")
            text = str(value).replace('"', '""')
            values.append(f'"{text}"')
        lines.append(",".join(values))
    return ("\n".join(lines)).encode("utf-8")


def build_submission_zip(meta_result: dict) -> bytes:
    buffer = BytesIO()
    project_id = meta_result.get("project_id", "meta_project")
    folder = f"submission_{project_id}"

    docx_bytes = build_meta_docx(meta_result)
    json_payload = json.dumps(meta_result, ensure_ascii=False, indent=2).encode("utf-8")
    forest_svg = (meta_result.get("forest_plot_svg") or "").encode("utf-8")
    funnel_svg = (meta_result.get("funnel_plot_svg") or "").encode("utf-8")
    narrative = (meta_result.get("narrative_results") or "").encode("utf-8")
    effects_csv = _effects_to_csv(meta_result)
    readme = (
        "Pacote de submissão de metanálise\n\n"
        "Arquivos incluídos:\n"
        "- manuscrito_meta_analise.docx: versão textual para edição e submissão.\n"
        "- meta_result_master.json: objeto estatístico completo e rastreável.\n"
        "- plots/forest_plot.svg: forest plot vetorial.\n"
        "- plots/funnel_plot.svg: funnel plot vetorial.\n"
        "- narrative_results.txt: síntese narrativa principal.\n"
    ).encode("utf-8")

    with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{folder}/README.txt", readme)
        zip_file.writestr(f"{folder}/manuscrito_meta_analise.docx", docx_bytes)
        zip_file.writestr(f"{folder}/meta_result_master.json", json_payload)
        zip_file.writestr(f"{folder}/effects_table.csv", effects_csv)
        if forest_svg:
            zip_file.writestr(f"{folder}/plots/forest_plot.svg", forest_svg)
        if funnel_svg:
            zip_file.writestr(f"{folder}/plots/funnel_plot.svg", funnel_svg)
        if narrative:
            zip_file.writestr(f"{folder}/narrative_results.txt", narrative)

    return buffer.getvalue()

