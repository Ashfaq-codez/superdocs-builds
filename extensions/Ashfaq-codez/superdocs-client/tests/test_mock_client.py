import unittest

from superdocs_client.exceptions import (
    ApprovalError,
    EditProposalError,
    ExportError,
)
from superdocs_client.mock_client import MockSuperDocsClient
from superdocs_client.models import ApprovalDecision, DocumentRef, ExportFormat


class TestMockSuperDocsClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = MockSuperDocsClient()

    # 1. upload success
    async def test_upload_success(self) -> None:
        doc = await self.client.upload("test.docx")
        self.assertIsInstance(doc, DocumentRef)
        self.assertTrue(doc.document_id.startswith("doc_"))

    # 2. propose_edit success
    async def test_propose_edit_success(self) -> None:
        doc = await self.client.upload("test.docx")
        prop = await self.client.propose_edit(doc, "Add clause")
        self.assertEqual(prop.document_id, doc.document_id)
        self.assertEqual(prop.status, "PENDING")

    # 3. propose_edit unknown document
    async def test_propose_edit_unknown_document(self) -> None:
        bad_doc = DocumentRef(document_id="doc_missing")
        with self.assertRaises(EditProposalError):
            await self.client.propose_edit(bad_doc, "Add clause")

    # 4. approve success
    async def test_approve_success(self) -> None:
        doc = await self.client.upload("test.docx")
        prop = await self.client.propose_edit(doc, "Add clause")
        res = await self.client.approve_edit(prop.proposal_id, ApprovalDecision.APPROVE)
        self.assertEqual(res.status, "APPROVE")
        self.assertTrue(res.applied)

    # 5. reject success
    async def test_reject_success(self) -> None:
        doc = await self.client.upload("test.docx")
        prop = await self.client.propose_edit(doc, "Add clause")
        res = await self.client.approve_edit(prop.proposal_id, ApprovalDecision.REJECT)
        self.assertEqual(res.status, "REJECT")
        self.assertFalse(res.applied)

    # 6. approving unknown proposal
    async def test_approving_unknown_proposal(self) -> None:
        with self.assertRaises(ApprovalError):
            await self.client.approve_edit("prop_missing", ApprovalDecision.APPROVE)

    # 7. resolving already-resolved proposal
    async def test_resolving_already_resolved_proposal(self) -> None:
        doc = await self.client.upload("test.docx")
        prop = await self.client.propose_edit(doc, "Add clause")
        await self.client.approve_edit(prop.proposal_id, ApprovalDecision.APPROVE)
        with self.assertRaises(ApprovalError):
            await self.client.approve_edit(prop.proposal_id, ApprovalDecision.REJECT)

    # 8. invalid approval decision
    async def test_invalid_approval_decision(self) -> None:
        doc = await self.client.upload("test.docx")
        prop = await self.client.propose_edit(doc, "Add clause")
        with self.assertRaises(ApprovalError):
            await self.client.approve_edit(prop.proposal_id, "APPROVE")  # type: ignore

    # 9. export PDF
    async def test_export_pdf(self) -> None:
        doc = await self.client.upload("test.docx")
        res = await self.client.export(doc, [ExportFormat.PDF])
        self.assertEqual(len(res.artifacts), 1)
        self.assertEqual(res.artifacts[0].format, ExportFormat.PDF)
        self.assertEqual(res.artifacts[0].reference, f"mock://exports/{doc.document_id}.pdf")

    # 10. export DOCX
    async def test_export_docx(self) -> None:
        doc = await self.client.upload("test.docx")
        res = await self.client.export(doc, [ExportFormat.DOCX])
        self.assertEqual(len(res.artifacts), 1)
        self.assertEqual(res.artifacts[0].format, ExportFormat.DOCX)
        self.assertEqual(res.artifacts[0].reference, f"mock://exports/{doc.document_id}.docx")

    # 11. export multiple formats
    async def test_export_multiple_formats(self) -> None:
        doc = await self.client.upload("test.docx")
        res = await self.client.export(doc, [ExportFormat.PDF, ExportFormat.DOCX])
        self.assertEqual(len(res.artifacts), 2)

    # 12. export unknown document
    async def test_export_unknown_document(self) -> None:
        bad_doc = DocumentRef(document_id="doc_missing")
        with self.assertRaises(ExportError):
            await self.client.export(bad_doc, [ExportFormat.PDF])

    # 13. invalid export format
    async def test_invalid_export_format(self) -> None:
        doc = await self.client.upload("test.docx")
        with self.assertRaises(ExportError):
            await self.client.export(doc, ["PDF"])  # type: ignore

    # 14. state isolation between two MockSuperDocsClient instances
    async def test_state_isolation(self) -> None:
        client1 = MockSuperDocsClient()
        client2 = MockSuperDocsClient()
        
        doc1 = await client1.upload("test.docx")
        
        # client2 should not know about doc1
        with self.assertRaises(EditProposalError):
            await client2.propose_edit(doc1, "Add clause")


if __name__ == "__main__":
    unittest.main()