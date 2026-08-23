import unittest

from backend.models.domain import AssembledDocument, AssembledSection
from backend.services.adapter import SuperDocsAdapter


class TestSuperDocsAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SuperDocsAdapter()

    def test_format_instruction_empty(self):
        doc = AssembledDocument(sections=[])
        result = self.adapter.format_instruction(doc)
        self.assertEqual(result, "")

    def test_format_instruction_single_section(self):
        doc = AssembledDocument(sections=[
            AssembledSection(
                source_clause_id="A",
                title="Employment Terms",
                paragraphs=["Paragraph 1.", "Paragraph 2."],
                page_break_before=False
            )
        ])
        result = self.adapter.format_instruction(doc)
        expected = "# Employment Terms\n\nParagraph 1.\n\nParagraph 2."
        self.assertEqual(result, expected)

    def test_format_instruction_with_page_break(self):
        doc = AssembledDocument(sections=[
            AssembledSection(
                source_clause_id="B",
                title="Confidentiality",
                paragraphs=["Confidentiality body."],
                page_break_before=True
            )
        ])
        result = self.adapter.format_instruction(doc)
        expected = "[PAGE BREAK]\n\n# Confidentiality\n\nConfidentiality body."
        self.assertEqual(result, expected)

    def test_format_instruction_multiple_sections(self):
        doc = AssembledDocument(sections=[
            AssembledSection(
                source_clause_id="A",
                title="Section A",
                paragraphs=["Body A"],
                page_break_before=False
            ),
            AssembledSection(
                source_clause_id="B",
                title="Section B",
                paragraphs=["Body B"],
                page_break_before=False
            )
        ])
        result = self.adapter.format_instruction(doc)
        expected = "# Section A\n\nBody A\n\n---\n\n# Section B\n\nBody B"
        self.assertEqual(result, expected)

    def test_format_instruction_preserves_duplicates(self):
        section = AssembledSection(
            source_clause_id="A",
            title="Duplicate Section",
            paragraphs=["Body content"],
            page_break_before=False
        )
        doc = AssembledDocument(sections=[section, section])
        result = self.adapter.format_instruction(doc)
        expected = "# Duplicate Section\n\nBody content\n\n---\n\n# Duplicate Section\n\nBody content"
        self.assertEqual(result, expected)

    def test_format_instruction_no_title(self):
        doc = AssembledDocument(sections=[
            AssembledSection(
                source_clause_id="A",
                title="",
                paragraphs=["Just a paragraph without a title."],
                page_break_before=False
            )
        ])
        result = self.adapter.format_instruction(doc)
        self.assertEqual(result, "Just a paragraph without a title.")


if __name__ == "__main__":
    unittest.main()