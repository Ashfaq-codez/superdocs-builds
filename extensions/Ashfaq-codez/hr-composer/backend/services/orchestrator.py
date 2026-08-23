import json
import uuid
from pathlib import Path
from typing import Dict, List

from backend.core.exceptions import (
    ComposerNotFoundError, 
    ConfigurationError, 
    InvalidStateTransitionError
)
from backend.models.domain import (
    ComposerRecord, 
    ComposerState, 
    HRRecord, 
    TemplateDefinition
)
from backend.services.jurisdiction import JurisdictionEngine
from backend.services.templating import TemplateEngine

from superdocs_client.interface import SuperDocsClientInterface
from superdocs_client.models import ApprovalDecision, DocumentRef, ExportFormat


class ComposerOrchestrator:
    """Coordinates the HR Composer workflow, templates, and SuperDocs integration."""

    def __init__(
        self,
        jurisdiction_engine: JurisdictionEngine,
        template_engine: TemplateEngine,
        superdocs_client: SuperDocsClientInterface,
        state_store: Dict[str, ComposerRecord],
        templates_base_path: Path
    ):
        self.jurisdiction_engine = jurisdiction_engine
        self.template_engine = template_engine
        self.superdocs_client = superdocs_client
        self.state_store = state_store
        self.templates_base_path = templates_base_path.resolve()
        
        self.registry_path = self.templates_base_path / "registry.json"
        self.blank_document_path = str(self.templates_base_path / "blank_offer.docx")

    def _load_template_def(self, jurisdiction_val: str) -> TemplateDefinition:
        """Reads the registry and loads the correct JSON template definition."""
        if not self.registry_path.exists():
            raise ConfigurationError("Template registry.json is missing.")
            
        with open(self.registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
            
        if jurisdiction_val not in registry:
            raise ConfigurationError(f"No template registered for jurisdiction: {jurisdiction_val}")
            
        template_file_path = (self.templates_base_path / registry[jurisdiction_val]).resolve()
        
        if not template_file_path.exists():
            raise ConfigurationError(f"Template file missing at {template_file_path}")
            
        with open(template_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return TemplateDefinition.model_validate(data)

    async def compose_document(self, hr_record: HRRecord) -> ComposerRecord:
        """Executes the pipeline from HR record to SuperDocs review gate."""
        comp_id = f"cmp_{uuid.uuid4().hex[:8]}"
        record = ComposerRecord(
            composition_id=comp_id,
            status=ComposerState.COMPOSING,
            hr_record=hr_record
        )
        self.state_store[comp_id] = record

        # 1. Resolve Jurisdiction
        jurisdiction = self.jurisdiction_engine.resolve(hr_record.location)
        
        # 2. Load Template
        template_def = self._load_template_def(jurisdiction.value)
        
        # 3. Populate Document deterministically
        composed_doc = self.template_engine.populate(hr_record, template_def)
        record.composed_document = composed_doc
        
        # 4. SuperDocs SDK Integration (Upload base + Propose edits)
        doc_ref = await self.superdocs_client.upload(self.blank_document_path)
        proposal = await self.superdocs_client.propose_edit(doc_ref, composed_doc.body)
        
        # 5. Halt at Review Gate
        record.document_id = doc_ref.document_id
        record.proposal_id = proposal.proposal_id
        record.status = ComposerState.REVIEW_REQUIRED
        
        return record

    def get_composition(self, composition_id: str) -> ComposerRecord:
        if composition_id not in self.state_store:
            raise ComposerNotFoundError(f"Composition '{composition_id}' not found.")
        return self.state_store[composition_id]

    async def submit_decision(self, composition_id: str, decision: ApprovalDecision) -> ComposerRecord:
        """Applies a human review decision."""
        record = self.get_composition(composition_id)
        
        if record.status != ComposerState.REVIEW_REQUIRED:
            raise InvalidStateTransitionError(
                f"Cannot submit decision. Status is {record.status.value}, expected REVIEW_REQUIRED."
            )
            
        await self.superdocs_client.approve_edit(record.proposal_id, decision)
        
        if decision == ApprovalDecision.APPROVE:
            record.status = ComposerState.APPROVED
        else:
            record.status = ComposerState.REJECTED
            
        return record

    async def export_composition(self, composition_id: str, formats: List[ExportFormat]) -> ComposerRecord:
        """Exports the approved document."""
        record = self.get_composition(composition_id)
        
        if record.status != ComposerState.APPROVED:
            raise InvalidStateTransitionError(
                f"Cannot export. Status is {record.status.value}, expected APPROVED."
            )
            
        export_result = await self.superdocs_client.export(DocumentRef(document_id=record.document_id), formats)
        
        record.artifacts = [
            {"format": a.format.value, "reference": a.reference} 
            for a in export_result.artifacts
        ]
        record.status = ComposerState.EXPORTED
        
        return record