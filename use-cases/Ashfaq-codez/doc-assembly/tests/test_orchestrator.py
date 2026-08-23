import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.core.exceptions import AssemblyNotFoundError, InvalidStateTransitionError
from backend.models.domain import AssemblyState
from backend.services.assembler import AssemblyEngine
from backend.services.adapter import SuperDocsAdapter
from backend.services.resolver import ClauseResolver
from backend.services.orchestrator import OrchestrationService

from superdocs_client.mock_client import MockSuperDocsClient
from superdocs_client.models import ApprovalDecision, ExportFormat


class TestOrchestrationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # 1. Setup offline file fixtures for the Resolver
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.clauses_dir = self.base_path / "clauses"
        self.clauses_dir.mkdir()
        
        with open(self.clauses_dir / "c1.json", "w") as f:
            json.dump({
                "id": "C1", "version": "1.0", "title": "Title C1", "body": "Body C1",
                "formatting_hints": {"style": "Standard", "page_break_before": False}
            }, f)
        with open(self.base_path / "registry.json", "w") as f:
            json.dump({"C1": "clauses/c1.json"}, f)
            
        # 2. Initialize all decoupled dependencies
        self.resolver = ClauseResolver(self.base_path)
        self.assembler = AssemblyEngine()
        self.adapter = SuperDocsAdapter()
        self.sdk = MockSuperDocsClient()
        self.state_store = {}
        
        # 3. Inject them into the Orchestrator
        self.orchestrator = OrchestrationService(
            resolver=self.resolver,
            assembler=self.assembler,
            adapter=self.adapter,
            superdocs_client=self.sdk,
            state_store=self.state_store
        )

    async def asyncTearDown(self):
        self.temp_dir.cleanup()

    async def test_successful_assembly_lifecycle(self):
        # Phase 1: Creation and SDK proposal (Includes checking duplicate preservation)
        record = await self.orchestrator.create_assembly(["C1", "C1"]) 
        self.assertEqual(record.status, AssemblyState.REVIEW_REQUIRED)
        self.assertIsNotNone(record.document_id)
        self.assertIsNotNone(record.proposal_id)
        
        # Phase 2: Explicit Human Approval
        approved_record = await self.orchestrator.submit_decision(record.assembly_id, ApprovalDecision.APPROVE)
        self.assertEqual(approved_record.status, AssemblyState.APPROVED)
        
        # Phase 3: Export 
        exported_record = await self.orchestrator.export_assembly(record.assembly_id, [ExportFormat.PDF])
        self.assertEqual(exported_record.status, AssemblyState.EXPORTED)
        self.assertEqual(len(exported_record.artifacts), 1)
        self.assertEqual(exported_record.artifacts[0]["format"], "PDF")
        self.assertTrue(exported_record.artifacts[0]["reference"].startswith("mock://"))

    async def test_rejection_lifecycle_blocks_export(self):
        record = await self.orchestrator.create_assembly(["C1"])
        
        rejected_record = await self.orchestrator.submit_decision(record.assembly_id, ApprovalDecision.REJECT)
        self.assertEqual(rejected_record.status, AssemblyState.REJECTED)
        
        # Attempting to export a rejected document MUST throw an error
        with self.assertRaises(InvalidStateTransitionError):
            await self.orchestrator.export_assembly(record.assembly_id, [ExportFormat.PDF])

    async def test_export_blocked_before_approval(self):
        record = await self.orchestrator.create_assembly(["C1"])
        self.assertEqual(record.status, AssemblyState.REVIEW_REQUIRED)
        
        # Attempting to export an unapproved document MUST throw an error
        with self.assertRaises(InvalidStateTransitionError):
            await self.orchestrator.export_assembly(record.assembly_id, [ExportFormat.PDF])

    async def test_invalid_approval_transition(self):
        record = await self.orchestrator.create_assembly(["C1"])
        await self.orchestrator.submit_decision(record.assembly_id, ApprovalDecision.APPROVE)
        
        # Cannot approve an assembly that is already approved
        with self.assertRaises(InvalidStateTransitionError):
            await self.orchestrator.submit_decision(record.assembly_id, ApprovalDecision.APPROVE)

    async def test_unknown_assembly(self):
        with self.assertRaises(AssemblyNotFoundError):
            self.orchestrator.get_assembly("invalid_id")


if __name__ == "__main__":
    unittest.main()