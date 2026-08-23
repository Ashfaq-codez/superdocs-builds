import uuid
from typing import Dict, List

from backend.core.exceptions import AssemblyNotFoundError, InvalidStateTransitionError
from backend.models.domain import AssemblyRecord, AssemblyState
from backend.services.resolver import ClauseResolver
from backend.services.assembler import AssemblyEngine
from backend.services.adapter import SuperDocsAdapter

from superdocs_client.interface import SuperDocsClientInterface
from superdocs_client.models import ApprovalDecision, ExportFormat, DocumentRef


class OrchestrationService:
    """Coordinates the document assembly workflow, enforcing the human review gate."""

    def __init__(
        self,
        resolver: ClauseResolver,
        assembler: AssemblyEngine,
        adapter: SuperDocsAdapter,
        superdocs_client: SuperDocsClientInterface,
        state_store: Dict[str, AssemblyRecord]
    ):
        self.resolver = resolver
        self.assembler = assembler
        self.adapter = adapter
        self.superdocs_client = superdocs_client
        self.state_store = state_store

    async def create_assembly(self, clause_ids: List[str]) -> AssemblyRecord:
        """Executes the pipeline from raw IDs up to the SuperDocs review gate."""
        assembly_id = f"asm_{uuid.uuid4().hex[:8]}"
        record = AssemblyRecord(
            assembly_id=assembly_id,
            status=AssemblyState.ASSEMBLING,
            requested_clauses=clause_ids
        )
        self.state_store[assembly_id] = record

        # 1. Resolve domain objects (will raise if invalid or duplicate checks fail)
        clauses = self.resolver.resolve(clause_ids)
        
        # 2. Assemble into intermediate document representation
        assembled_doc = self.assembler.assemble(clauses)
        
        # 3. Serialize to SuperDocs-specific instruction format
        instruction = self.adapter.format_instruction(assembled_doc)
        
        # 4. Upload base template (Fulfills the Phase 1 SDK requirement)
        doc_ref = await self.superdocs_client.upload("templates/blank_branded_template.docx")
        
        # 5. Propose the generated text to SuperDocs
        proposal = await self.superdocs_client.propose_edit(doc_ref, instruction)
        
        # 6. Halt workflow at the review gate
        record.document_id = doc_ref.document_id
        record.proposal_id = proposal.proposal_id
        record.status = AssemblyState.REVIEW_REQUIRED
        
        return record

    def get_assembly(self, assembly_id: str) -> AssemblyRecord:
        """Retrieves a specific assembly from the state store."""
        if assembly_id not in self.state_store:
            raise AssemblyNotFoundError(f"Assembly '{assembly_id}' not found.")
        return self.state_store[assembly_id]

    async def submit_decision(self, assembly_id: str, decision: ApprovalDecision) -> AssemblyRecord:
        """Applies a human review decision to the assembly."""
        record = self.get_assembly(assembly_id)
        
        # HARD GUARD: Only pending proposals can be reviewed
        if record.status != AssemblyState.REVIEW_REQUIRED:
            raise InvalidStateTransitionError(
                f"Cannot submit decision. Assembly is currently in state '{record.status.value}', expected REVIEW_REQUIRED."
            )
            
        await self.superdocs_client.approve_edit(record.proposal_id, decision)
        
        if decision == ApprovalDecision.APPROVE:
            record.status = AssemblyState.APPROVED
        else:
            record.status = AssemblyState.REJECTED
            
        return record

    async def export_assembly(self, assembly_id: str, formats: List[ExportFormat]) -> AssemblyRecord:
        """Exports the approved document from SuperDocs."""
        record = self.get_assembly(assembly_id)
        
        # HARD GUARD: Never export an unapproved document
        if record.status != AssemblyState.APPROVED:
            raise InvalidStateTransitionError(
                f"Cannot export. Assembly is currently in state '{record.status.value}', expected APPROVED."
            )
            
        export_result = await self.superdocs_client.export(DocumentRef(document_id=record.document_id), formats)
        
        # Translate the SDK's ExportArtifact objects into simple dictionaries for the record
        record.artifacts = [
            {"format": a.format.value, "reference": a.reference} 
            for a in export_result.artifacts
        ]
        record.status = AssemblyState.EXPORTED
        
        return record