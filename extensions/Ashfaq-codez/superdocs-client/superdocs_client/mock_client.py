import uuid
from typing import Dict, List, Set

from .exceptions import (
    ApprovalError,
    DocumentUploadError,
    EditProposalError,
    ExportError,
)
from .interface import SuperDocsClientInterface
from .models import (
    ApprovalDecision,
    ApprovalResult,
    DocumentRef,
    EditProposal,
    ExportArtifact,
    ExportFormat,
    ExportResult,
)


class MockSuperDocsClient(SuperDocsClientInterface):
    """Mock client enforcing domain workflows with isolated state."""

    def __init__(self) -> None:
        self._documents: Set[str] = set()
        self._proposals: Dict[str, EditProposal] = {}
        self._proposal_status: Dict[str, str] = {}

    def _generate_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    async def upload(self, file_path: str) -> DocumentRef:
        if not file_path:
            raise DocumentUploadError("File path cannot be empty.")
            
        doc_id = self._generate_id("doc")
        self._documents.add(doc_id)
        return DocumentRef(document_id=doc_id)

    async def propose_edit(self, document: DocumentRef, instruction: str) -> EditProposal:
        if not isinstance(document, DocumentRef):
            raise EditProposalError("document must be a DocumentRef.")
            
        if document.document_id not in self._documents:
            raise EditProposalError(f"Unknown document: {document.document_id}")

        prop_id = self._generate_id("prop")
        proposal = EditProposal(
            proposal_id=prop_id,
            document_id=document.document_id,
            proposed_changes={"mock_diff": f"Instruction applied: {instruction}"},
            status="PENDING"
        )
        self._proposals[prop_id] = proposal
        self._proposal_status[prop_id] = "PENDING"
        
        return proposal

    async def approve_edit(
        self, proposal_id: str, decision: ApprovalDecision
    ) -> ApprovalResult:
        if proposal_id not in self._proposals:
            raise ApprovalError(f"Unknown proposal: {proposal_id}")
            
        if not isinstance(decision, ApprovalDecision):
            raise ApprovalError(f"Invalid decision type: {decision}")
            
        current_status = self._proposal_status[proposal_id]
        if current_status != "PENDING":
            raise ApprovalError(f"Proposal is already resolved with status: {current_status}")

        self._proposal_status[proposal_id] = decision.value
        
        return ApprovalResult(
            proposal_id=proposal_id,
            status=decision.value,
            applied=(decision == ApprovalDecision.APPROVE)
        )

    async def export(
        self, document: DocumentRef, formats: List[ExportFormat]
    ) -> ExportResult:
        if not isinstance(document, DocumentRef):
            raise ExportError("document must be a DocumentRef.")
            
        if document.document_id not in self._documents:
            raise ExportError(f"Unknown document: {document.document_id}")

        artifacts: List[ExportArtifact] = []
        for fmt in formats:
            if not isinstance(fmt, ExportFormat):
                raise ExportError(f"Invalid format: {fmt}")
                
            extension = fmt.value.lower()
            ref = f"mock://exports/{document.document_id}.{extension}"
            artifacts.append(ExportArtifact(format=fmt, reference=ref))

        return ExportResult(
            document_id=document.document_id,
            artifacts=artifacts,
            status="COMPLETED"
        )