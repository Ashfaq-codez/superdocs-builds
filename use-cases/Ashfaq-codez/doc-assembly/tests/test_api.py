import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.dependencies import get_orchestrator
from backend.services.resolver import ClauseResolver
from backend.services.assembler import AssemblyEngine
from backend.services.adapter import SuperDocsAdapter
from backend.services.orchestrator import OrchestrationService

from superdocs_client.mock_client import MockSuperDocsClient


class TestDocumentAssemblyAPI(unittest.TestCase):
    def setUp(self):
        # Setup offline file fixtures
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.clauses_dir = self.base_path / "clauses"
        self.clauses_dir.mkdir()
        
        with open(self.clauses_dir / "c1.json", "w") as f:
            json.dump({
                "id": "C1", "version": "1.0", "title": "C1", "body": "Body",
                "formatting_hints": {"style": "S", "page_break_before": False}
            }, f)
        with open(self.base_path / "registry.json", "w") as f:
            json.dump({"C1": "clauses/c1.json"}, f)
            
        # Create an isolated Orchestrator for the TestClient
        test_orchestrator = OrchestrationService(
            resolver=ClauseResolver(self.base_path),
            assembler=AssemblyEngine(),
            adapter=SuperDocsAdapter(),
            superdocs_client=MockSuperDocsClient(),
            state_store={}
        )
        
        # Override the FastAPI dependency
        app.dependency_overrides[get_orchestrator] = lambda: test_orchestrator
        self.client = TestClient(app)

    def tearDown(self):
        self.temp_dir.cleanup()
        app.dependency_overrides.clear()

    def test_full_successful_api_workflow(self):
        # 1. Assemble
        create_resp = self.client.post("/assemblies", json={"clause_ids": ["C1"]})
        self.assertEqual(create_resp.status_code, 201)
        data = create_resp.json()
        assembly_id = data["assembly_id"]
        self.assertEqual(data["status"], "REVIEW_REQUIRED")
        
        # 2. Check Get
        get_resp = self.client.get(f"/assemblies/{assembly_id}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["status"], "REVIEW_REQUIRED")
        
        # 3. Approve
        approve_resp = self.client.post(f"/assemblies/{assembly_id}/approve")
        self.assertEqual(approve_resp.status_code, 200)
        self.assertEqual(approve_resp.json()["status"], "APPROVED")
        
        # 4. Export
        export_resp = self.client.post(f"/assemblies/{assembly_id}/export", json={"formats": ["PDF"]})
        self.assertEqual(export_resp.status_code, 200)
        self.assertEqual(export_resp.json()["status"], "EXPORTED")

    def test_export_blocked_by_human_gate(self):
        # Create assembly, leaving it in REVIEW_REQUIRED
        create_resp = self.client.post("/assemblies", json={"clause_ids": ["C1"]})
        assembly_id = create_resp.json()["assembly_id"]
        
        # Attempt export directly
        export_resp = self.client.post(f"/assemblies/{assembly_id}/export", json={"formats": ["PDF"]})
        
        # Should be blocked by HTTP 409 Conflict (InvalidStateTransitionError)
        self.assertEqual(export_resp.status_code, 409)

    def test_unknown_clause_returns_404(self):
        resp = self.client.post("/assemblies", json={"clause_ids": ["MISSING"]})
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()