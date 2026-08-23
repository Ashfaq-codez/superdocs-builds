import unittest
from backend.services.jurisdiction import JurisdictionEngine
from backend.models.domain import Jurisdiction
from backend.core.exceptions import UnsupportedJurisdictionError


class TestJurisdictionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = JurisdictionEngine()

    def test_valid_locations(self):
        self.assertEqual(self.engine.resolve("San Francisco, CA"), Jurisdiction.CALIFORNIA)
        self.assertEqual(self.engine.resolve("london "), Jurisdiction.UK)

    def test_unsupported_location(self):
        with self.assertRaises(UnsupportedJurisdictionError):
            self.engine.resolve("Paris, France")

    def test_empty_location(self):
        with self.assertRaises(UnsupportedJurisdictionError):
            self.engine.resolve("")