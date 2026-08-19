import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.core.exceptions import (
    ClauseNotFoundError,
    InvalidRequestError,
    LibraryConfigurationError,
)
from backend.services.resolver import ClauseResolver


class TestClauseResolver(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        self.clauses_dir = self.base_path / "clauses"
        self.clauses_dir.mkdir()
        
        # Setup valid clauses
        self.clause_a_path = self.clauses_dir / "a.json"
        self.clause_b_path = self.clauses_dir / "b.json"
        
        self.clause_a_data = {
            "id": "A", "version": "1.0", "title": "Title A", "body": "Body A",
            "formatting_hints": {"style": "Standard", "page_break_before": False}
        }
        self.clause_b_data = {
            "id": "B", "version": "1.0", "title": "Title B", "body": "Body B",
            "formatting_hints": {"style": "Standard", "page_break_before": False}
        }
        
        with open(self.clause_a_path, "w") as f: json.dump(self.clause_a_data, f)
        with open(self.clause_b_path, "w") as f: json.dump(self.clause_b_data, f)
        
        # Setup specific broken files for testing errors
        self.broken_json_path = self.clauses_dir / "broken.json"
        with open(self.broken_json_path, "w") as f: f.write("{bad_json: true,}")
            
        self.invalid_model_path = self.clauses_dir / "invalid_model.json"
        with open(self.invalid_model_path, "w") as f: 
            json.dump({"id": "BAD", "version": "1.0"}, f) # Missing required fields
        
        # Setup Registry
        self.registry_data = {
            "B": "clauses/b.json",  # Ordered backwards in JSON intentionally
            "A": "clauses/a.json",
            "MISSING_FILE": "clauses/missing.json",
            "MALFORMED_JSON": "clauses/broken.json",
            "INVALID_MODEL": "clauses/invalid_model.json",
            "TRAVERSAL": "../../../etc/passwd"
        }
        self.registry_path = self.base_path / "registry.json"
        with open(self.registry_path, "w") as f: json.dump(self.registry_data, f)
        
        # Initialize resolver
        self.resolver = ClauseResolver(self.base_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_valid_single_clause(self):
        res = self.resolver.resolve(["A"])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].id, "A")
        self.assertEqual(res[0].title, "Title A")

    def test_valid_multiple_clauses(self):
        res = self.resolver.resolve(["A", "B"])
        self.assertEqual(len(res), 2)

    def test_exact_requested_ordering(self):
        # Even though registry has B then A, requesting A then B returns exactly A then B
        res = self.resolver.resolve(["A", "B"])
        self.assertEqual(res[0].id, "A")
        self.assertEqual(res[1].id, "B")
        
        # Reverse request
        res_reverse = self.resolver.resolve(["B", "A"])
        self.assertEqual(res_reverse[0].id, "B")
        self.assertEqual(res_reverse[1].id, "A")

    def test_registry_ordering_does_not_affect_result(self):
        # Covered implicitly by test_exact_requested_ordering, but explicitly asserting:
        res = self.resolver.resolve(["A", "B"])
        self.assertEqual([c.id for c in res], ["A", "B"])

    def test_unknown_id(self):
        with self.assertRaises(ClauseNotFoundError):
            self.resolver.resolve(["UNKNOWN"])

    # REMOVE test_duplicate_ids and ADD this:
    def test_duplicate_ids_preserve_requested_order(self):
        # Requesting A -> B -> A must return exactly A -> B -> A
        res = self.resolver.resolve(["A", "B", "A"])
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0].id, "A")
        self.assertEqual(res[1].id, "B")
        self.assertEqual(res[2].id, "A")

    def test_empty_input(self):
        with self.assertRaises(InvalidRequestError):
            self.resolver.resolve([])

    def test_blank_ids(self):
        with self.assertRaises(InvalidRequestError):
            self.resolver.resolve([" "])

    def test_missing_clause_file(self):
        with self.assertRaises(LibraryConfigurationError) as context:
            self.resolver.resolve(["MISSING_FILE"])
        self.assertIn("File missing", str(context.exception))

    def test_malformed_json(self):
        with self.assertRaises(LibraryConfigurationError) as context:
            self.resolver.resolve(["MALFORMED_JSON"])
        self.assertIn("Malformed JSON", str(context.exception))

    def test_invalid_clause_definition(self):
        with self.assertRaises(LibraryConfigurationError) as context:
            self.resolver.resolve(["INVALID_MODEL"])
        self.assertIn("Invalid ClauseDefinition data", str(context.exception))

    def test_path_traversal(self):
        with self.assertRaises(LibraryConfigurationError) as context:
            self.resolver.resolve(["TRAVERSAL"])
        self.assertIn("Path traversal detected", str(context.exception))


if __name__ == "__main__":
    unittest.main()