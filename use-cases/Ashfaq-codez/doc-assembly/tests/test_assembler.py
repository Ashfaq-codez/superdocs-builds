import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from backend.core.exceptions import ClauseFormatError, EmptyAssemblyError
from backend.models.domain import ClauseDefinition, FormattingHints
from backend.services.assembler import AssemblyEngine
from backend.services.resolver import ClauseResolver


class TestAssemblyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AssemblyEngine()

        self.clause_a = ClauseDefinition(
            id="A", version="1.0", title="Title A", body="Body A.",
            formatting_hints=FormattingHints(style="Standard", page_break_before=False)
        )
        self.clause_b = ClauseDefinition(
            id="B", version="1.0", title="Title B", body="Body B.",
            formatting_hints=FormattingHints(style="Standard", page_break_before=True)
        )

    def test_single_clause_assembly(self):
        doc = self.engine.assemble([self.clause_a])
        self.assertEqual(len(doc.sections), 1)
        self.assertEqual(doc.sections[0].source_clause_id, "A")

    def test_multiple_clause_assembly(self):
        doc = self.engine.assemble([self.clause_a, self.clause_b])
        self.assertEqual(len(doc.sections), 2)

    def test_exact_requested_ordering(self):
        doc = self.engine.assemble([self.clause_b, self.clause_a])
        self.assertEqual(doc.sections[0].source_clause_id, "B")
        self.assertEqual(doc.sections[1].source_clause_id, "A")

    def test_repeated_clause_ids_preserve_order(self):
        doc = self.engine.assemble([self.clause_a, self.clause_b, self.clause_a])
        self.assertEqual(len(doc.sections), 3)
        self.assertEqual([s.source_clause_id for s in doc.sections], ["A", "B", "A"])

    def test_section_title_preservation(self):
        doc = self.engine.assemble([self.clause_a])
        self.assertEqual(doc.sections[0].title, "Title A")

    def test_paragraph_structure_preservation(self):
        c = ClauseDefinition(
            id="C", version="1.0", title="T",
            body="Para 1.\n\nPara 2.\n\n\nPara 3.",
            formatting_hints=FormattingHints(style="Standard", page_break_before=False)
        )
        doc = self.engine.assemble([c])
        self.assertEqual(len(doc.sections[0].paragraphs), 3)
        self.assertEqual(doc.sections[0].paragraphs[1], "Para 2.")

    def test_deterministic_whitespace_normalization(self):
        c = ClauseDefinition(
            id="C", version="1.0", title="  T  ",
            body="  Para 1.  \n\n  Para 2.  ",
            formatting_hints=FormattingHints(style="Standard", page_break_before=False)
        )
        doc = self.engine.assemble([c])
        self.assertEqual(doc.sections[0].title, "T")
        self.assertEqual(doc.sections[0].paragraphs, ["Para 1.", "Para 2."])

    def test_no_semantic_content_modification(self):
        body_text = "Verbatim 100% check! No commas removed, right?"
        c = ClauseDefinition(
            id="C", version="1.0", title="T", body=body_text,
            formatting_hints=FormattingHints(style="Standard", page_break_before=False)
        )
        doc = self.engine.assemble([c])
        self.assertEqual(doc.sections[0].paragraphs[0], body_text)

    def test_deterministic_identical_output(self):
        doc1 = self.engine.assemble([self.clause_a, self.clause_b])
        doc2 = self.engine.assemble([self.clause_a, self.clause_b])
        self.assertEqual(doc1.model_dump(), doc2.model_dump())

    def test_formatting_metadata_preservation(self):
        doc = self.engine.assemble([self.clause_b])
        self.assertTrue(doc.sections[0].page_break_before)

    def test_empty_assembly_rejection(self):
        with self.assertRaises(EmptyAssemblyError):
            self.engine.assemble([])

    def test_invalid_clause_definition_rejection(self):
        c = ClauseDefinition(
            id="BAD", version="1.0", title="", body="   ",
            formatting_hints=FormattingHints(style="Standard", page_break_before=False)
        )
        with self.assertRaises(ClauseFormatError):
            self.engine.assemble([c])

    def test_whitespace_only_body_behavior(self):
        c = ClauseDefinition(
            id="W", version="1.0", title="Valid Title", body="   \n\n  ",
            formatting_hints=FormattingHints(style="Standard", page_break_before=False)
        )
        doc = self.engine.assemble([c])
        self.assertEqual(doc.sections[0].title, "Valid Title")
        self.assertEqual(doc.sections[0].paragraphs, [])

    def test_resolver_to_assembler_integration(self):
        # Test full handoff offline using temporary registry
        with TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            clauses_dir = base_path / "clauses"
            clauses_dir.mkdir()
            
            with open(clauses_dir / "c1.json", "w") as f:
                json.dump({
                    "id": "C1", "version": "1.0", "title": "C1", "body": "Body C1",
                    "formatting_hints": {"style": "S", "page_break_before": False}
                }, f)
                
            with open(base_path / "registry.json", "w") as f:
                json.dump({"C1": "clauses/c1.json"}, f)
                
            resolver = ClauseResolver(base_path)
            resolved = resolver.resolve(["C1", "C1"])
            
            # Integration step
            doc = self.engine.assemble(resolved)
            self.assertEqual(len(doc.sections), 2)
            self.assertEqual(doc.sections[0].source_clause_id, "C1")
            self.assertEqual(doc.sections[1].source_clause_id, "C1")


if __name__ == "__main__":
    unittest.main()