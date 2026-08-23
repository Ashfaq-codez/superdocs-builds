from fastapi import APIRouter, Depends, status
from backend.core.dependencies import get_orchestrator
from backend.models.api import AssembleRequest, ExportRequest
from backend.models.domain import AssemblyRecord
from backend.services.orchestrator import OrchestrationService
from superdocs_client.models import ApprovalDecision

router = APIRouter(prefix="/assemblies", tags=["Assembly"])


@router.post("", response_model=AssemblyRecord, status_code=status.HTTP_201_CREATED)
async def create_assembly(
    request: AssembleRequest,
    orchestrator: OrchestrationService = Depends(get_orchestrator)
):
    """Receives clause IDs, assembles the document, and proposes it to SuperDocs for review."""
    return await orchestrator.create_assembly(request.clause_ids)


@router.get("/{assembly_id}", response_model=AssemblyRecord)
async def get_assembly(
    assembly_id: str,
    orchestrator: OrchestrationService = Depends(get_orchestrator)
):
    """Retrieves the current state of an assembly."""
    return orchestrator.get_assembly(assembly_id)


@router.post("/{assembly_id}/approve", response_model=AssemblyRecord)
async def approve_assembly(
    assembly_id: str,
    orchestrator: OrchestrationService = Depends(get_orchestrator)
):
    """Applies the human approval gate to the assembly."""
    return await orchestrator.submit_decision(assembly_id, ApprovalDecision.APPROVE)


@router.post("/{assembly_id}/reject", response_model=AssemblyRecord)
async def reject_assembly(
    assembly_id: str,
    orchestrator: OrchestrationService = Depends(get_orchestrator)
):
    """Rejects the assembly proposal."""
    return await orchestrator.submit_decision(assembly_id, ApprovalDecision.REJECT)


@router.post("/{assembly_id}/export", response_model=AssemblyRecord)
async def export_assembly(
    assembly_id: str,
    request: ExportRequest,
    orchestrator: OrchestrationService = Depends(get_orchestrator)
):
    """Exports the finalized document. Strictly requires the assembly to be in the APPROVED state."""
    return await orchestrator.export_assembly(assembly_id, request.formats)