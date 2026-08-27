import unittest
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from docx import Document

from superdocs_client.local_client import LocalSuperDocsClient
from superdocs_client.models import ApprovalDecision, ExportFormat
from superdocs_client.exceptions import ExportError

class TestLocalSuperDocsClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = TemporaryDirectory()
        self.client = LocalSuperDocsClient(Path(self.temp_dir.name))
        
        self.doc_ref = await self.client.upload("dummy.txt")
        self.proposal = await self.client.propose_edit(
            self.doc_ref, 
            "# Employment Offer\n## Candidate Details\nName: John Smith\nPosition: Developer\nCompensation: $150,000"
        )

    async def asyncTearDown(self):
        self.temp_dir.cleanup()

    async def test_export_fails_before_approval(self):
        with self.assertRaises(ExportError):
            await self.client.export(self.doc_ref, [ExportFormat.PDF])

    async def test_successful_export_generates_valid_files_with_content(self):
        # 1. Approve
        await self.client.approve_edit(self.proposal.proposal_id, ApprovalDecision.APPROVE)
        
        # 2. Export
        result = await self.client.export(self.doc_ref, [ExportFormat.DOCX, ExportFormat.PDF])
        self.assertEqual(len(result.artifacts), 2)
        
        docx_path = Path(self.temp_dir.name) / self.doc_ref.document_id / "offer_letter.docx"
        pdf_path = Path(self.temp_dir.name) / self.doc_ref.document_id / "offer_letter.pdf"
        
        # 3. Assert files physically exist
        self.assertTrue(docx_path.exists())
        self.assertTrue(pdf_path.exists())
        
        # 4. Assert DOCX is valid OpenXML and contains data
        doc = Document(str(docx_path))
        full_text = "\n".join([p.text for p in doc.paragraphs])
        self.assertIn("John Smith", full_text)
        self.assertIn("Developer", full_text)
        self.assertIn("$150,000", full_text)
        self.assertIn("SuperDocs Inc.", full_text) # Header should be applied

        # 5. Assert PDF is valid binary
        with open(pdf_path, 'rb') as f:
            pdf_header = f.read(5)
            self.assertEqual(pdf_header, b"%PDF-")

if __name__ == "__main__":
    unittest.main()