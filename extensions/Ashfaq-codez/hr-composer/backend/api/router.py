from fastapi import APIRouter, Depends, status
from backend.core.dependencies import get_orchestrator
from backend.models.api import ComposeRequest, ExportRequest, ComposerResponse
from backend.models.domain import ComposerRecord
from backend.services.orchestrator import ComposerOrchestrator
from superdocs_client.models import ApprovalDecision

router = APIRouter(prefix="/compositions", tags=["HR Composer"])


def _to_response(record: ComposerRecord) -> ComposerResponse:
    """Helper to convert the internal record to the public API contract."""
    doc = record.composed_document
    return ComposerResponse(
        composition_id=record.composition_id,
        status=record.status.value,
        jurisdiction_applied=doc.jurisdiction.value if doc else None,
        template_id_applied=doc.template_id if doc else None,
        document_id=record.document_id,
        artifacts=record.artifacts
    )


@router.post("", response_model=ComposerResponse, status_code=status.HTTP_201_CREATED)
async def compose_document(
    request: ComposeRequest,
    orchestrator: ComposerOrchestrator = Depends(get_orchestrator)
):
    record = await orchestrator.compose_document(request.hr_record)
    return _to_response(record)


@router.get("/{composition_id}", response_model=ComposerResponse)
async def get_composition(
    composition_id: str,
    orchestrator: ComposerOrchestrator = Depends(get_orchestrator)
):
    record = orchestrator.get_composition(composition_id)
    return _to_response(record)


@router.post("/{composition_id}/approve", response_model=ComposerResponse)
async def approve_composition(
    composition_id: str,
    orchestrator: ComposerOrchestrator = Depends(get_orchestrator)
):
    record = await orchestrator.submit_decision(composition_id, ApprovalDecision.APPROVE)
    return _to_response(record)


@router.post("/{composition_id}/reject", response_model=ComposerResponse)
async def reject_composition(
    composition_id: str,
    orchestrator: ComposerOrchestrator = Depends(get_orchestrator)
):
    record = await orchestrator.submit_decision(composition_id, ApprovalDecision.REJECT)
    return _to_response(record)


@router.post("/{composition_id}/export", response_model=ComposerResponse)
async def export_composition(
    composition_id: str,
    request: ExportRequest,
    orchestrator: ComposerOrchestrator = Depends(get_orchestrator)
):
    record = await orchestrator.export_composition(composition_id, request.formats)
    return _to_response(record)