import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.core.exceptions import ConfigurationError, InvalidStateTransitionError, ComposerNotFoundError
from backend.models.domain import ComposerState, HRRecord
from backend.services.jurisdiction import JurisdictionEngine
from backend.services.templating import TemplateEngine
from backend.services.orchestrator import ComposerOrchestrator

from superdocs_client.mock_client import MockSuperDocsClient
from superdocs_client.models import ApprovalDecision, ExportFormat


class TestComposerOrchestrator(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = TemporaryDirectory()
        self.templates_path = Path(self.temp_dir.name)
        (self.templates_path / "files").mkdir()
        (self.templates_path / "blank_offer.docx").touch()
        
        # Setup test registry and template
        with open(self.templates_path / "files/uk.json", "w") as f:
            json.dump({
                "id": "uk_test", "version": "1.0", "jurisdiction": "UK",
                "required_fields": ["candidate_name", "role", "salary"],
                "body_template": "Offer to $candidate_name for $role at $salary"
            }, f)
            
        with open(self.templates_path / "registry.json", "w") as f:
            json.dump({"UK": "files/uk.json"}, f)
            
        self.state_store = {}
        self.orchestrator = ComposerOrchestrator(
            jurisdiction_engine=JurisdictionEngine(),
            template_engine=TemplateEngine(),
            superdocs_client=MockSuperDocsClient(),
            state_store=self.state_store,
            templates_base_path=self.templates_path
        )
        
        self.hr_record = HRRecord(
            candidate_name="Alice", role="Dev", salary="$100k",
            location="London", start_date="2026-09-01"
        )

    async def asyncTearDown(self):
        self.temp_dir.cleanup()

    async def test_full_lifecycle_success(self):
        # 1. Compose -> REVIEW_REQUIRED
        record = await self.orchestrator.compose_document(self.hr_record)
        self.assertEqual(record.status, ComposerState.REVIEW_REQUIRED)
        self.assertIsNotNone(record.document_id)
        self.assertEqual(record.composed_document.jurisdiction, "UK")
        self.assertEqual(record.composed_document.body, "Offer to Alice for Dev at $100k")
        
        # 2. Approve -> APPROVED
        approved = await self.orchestrator.submit_decision(record.composition_id, ApprovalDecision.APPROVE)
        self.assertEqual(approved.status, ComposerState.APPROVED)
        
        # 3. Export -> EXPORTED
        exported = await self.orchestrator.export_composition(record.composition_id, [ExportFormat.PDF])
        self.assertEqual(exported.status, ComposerState.EXPORTED)
        self.assertEqual(len(exported.artifacts), 1)

    async def test_rejection_blocks_export(self):
        record = await self.orchestrator.compose_document(self.hr_record)
        await self.orchestrator.submit_decision(record.composition_id, ApprovalDecision.REJECT)
        
        with self.assertRaises(InvalidStateTransitionError):
            await self.orchestrator.export_composition(record.composition_id, [ExportFormat.PDF])

    async def test_export_blocked_before_approval(self):
        record = await self.orchestrator.compose_document(self.hr_record)
        
        with self.assertRaises(InvalidStateTransitionError):
            await self.orchestrator.export_composition(record.composition_id, [ExportFormat.PDF])

    async def test_missing_registry_raises_config_error(self):
        (self.templates_path / "registry.json").unlink() # Delete registry
        with self.assertRaises(ConfigurationError):
            await self.orchestrator.compose_document(self.hr_record)
            
    async def test_unknown_composition_id(self):
        with self.assertRaises(ComposerNotFoundError):
            self.orchestrator.get_composition("invalid_id")


if __name__ == "__main__":
    unittest.main()