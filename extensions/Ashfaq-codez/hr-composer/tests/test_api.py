import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.dependencies import get_orchestrator
from backend.services.jurisdiction import JurisdictionEngine
from backend.services.templating import TemplateEngine
from backend.services.orchestrator import ComposerOrchestrator

from superdocs_client.mock_client import MockSuperDocsClient


class TestHRComposerAPI(unittest.TestCase):
    def setUp(self):
        # 1. Isolate templates for the test
        self.temp_dir = TemporaryDirectory()
        self.templates_path = Path(self.temp_dir.name)
        (self.templates_path / "files").mkdir()
        (self.templates_path / "blank_offer.docx").touch()
        
        with open(self.templates_path / "files/california.json", "w") as f:
            json.dump({
                "id": "ca_test", "version": "1.0", "jurisdiction": "CALIFORNIA",
                "required_fields": ["candidate_name", "role", "salary"],
                "body_template": "CA Offer for $candidate_name ($role, $salary)"
            }, f)
            
        with open(self.templates_path / "registry.json", "w") as f:
            json.dump({"CALIFORNIA": "files/california.json"}, f)
            
        # 2. Setup orchestrator override
        test_orchestrator = ComposerOrchestrator(
            jurisdiction_engine=JurisdictionEngine(),
            template_engine=TemplateEngine(),
            superdocs_client=MockSuperDocsClient(),
            state_store={},
            templates_base_path=self.templates_path
        )
        app.dependency_overrides[get_orchestrator] = lambda: test_orchestrator
        self.client = TestClient(app)
        
        self.valid_hr_record = {
            "hr_record": {
                "candidate_name": "Bob",
                "role": "QA",
                "salary": "$80k",
                "location": "San Francisco, CA",
                "start_date": "2026-10-01"
            }
        }

    def tearDown(self):
        self.temp_dir.cleanup()
        app.dependency_overrides.clear()

    def test_full_successful_api_workflow(self):
        # 1. Compose -> 201 Created
        resp_compose = self.client.post("/compositions", json=self.valid_hr_record)
        self.assertEqual(resp_compose.status_code, 201)
        comp_id = resp_compose.json()["composition_id"]
        
        # 2. Get -> 200 OK
        resp_get = self.client.get(f"/compositions/{comp_id}")
        self.assertEqual(resp_get.status_code, 200)
        self.assertEqual(resp_get.json()["jurisdiction_applied"], "CALIFORNIA")
        self.assertEqual(resp_get.json()["status"], "REVIEW_REQUIRED")
        
        # 3. Approve -> 200 OK
        resp_approve = self.client.post(f"/compositions/{comp_id}/approve")
        self.assertEqual(resp_approve.status_code, 200)
        self.assertEqual(resp_approve.json()["status"], "APPROVED")
        
        # 4. Export -> 200 OK
        resp_export = self.client.post(f"/compositions/{comp_id}/export", json={"formats": ["PDF"]})
        self.assertEqual(resp_export.status_code, 200)
        self.assertEqual(resp_export.json()["status"], "EXPORTED")

    def test_missing_field_returns_422(self):
        bad_record = {"hr_record": self.valid_hr_record["hr_record"].copy()}
        del bad_record["hr_record"]["salary"] # missing required field
        
        resp = self.client.post("/compositions", json=bad_record)
        
        # FastAPI's Pydantic validation intercepts missing required fields
        # and automatically returns a 422 Unprocessable Entity.
        self.assertEqual(resp.status_code, 422)

    def test_export_blocked_by_human_gate(self):
        resp_compose = self.client.post("/compositions", json=self.valid_hr_record)
        comp_id = resp_compose.json()["composition_id"]
        
        resp_export = self.client.post(f"/compositions/{comp_id}/export", json={"formats": ["PDF"]})
        self.assertEqual(resp_export.status_code, 409) # InvalidStateTransitionError


if __name__ == "__main__":
    unittest.main()