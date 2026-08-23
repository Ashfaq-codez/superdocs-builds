import unittest
from backend.services.templating import TemplateEngine
from backend.models.domain import HRRecord, TemplateDefinition, Jurisdiction
from backend.core.exceptions import MissingTemplateFieldError


class TestTemplateEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TemplateEngine()
        self.record = HRRecord(
            candidate_name="Ashfaq",
            role="Software Engineer",
            salary="£60,000",
            location="London",
            start_date="2026-09-01"
        )
        self.template_def = TemplateDefinition(
            id="uk_standard_v1",
            version="1.0.0",
            jurisdiction=Jurisdiction.UK,
            required_fields=["candidate_name", "role", "salary"],
            body_template="Offer to $candidate_name for $role at $salary."
        )

    def test_successful_population(self):
        doc = self.engine.populate(self.record, self.template_def)
        self.assertEqual(doc.body, "Offer to Ashfaq for Software Engineer at £60,000.")
        self.assertEqual(doc.template_id, "uk_standard_v1")
        self.assertEqual(doc.jurisdiction, Jurisdiction.UK)

    def test_missing_required_field_in_definition(self):
        self.template_def.required_fields.append("bonus")
        with self.assertRaises(MissingTemplateFieldError):
            self.engine.populate(self.record, self.template_def)

    def test_missing_placeholder_in_record(self):
        self.template_def.body_template = "Offer to $candidate_name with $equity equity."
        with self.assertRaises(MissingTemplateFieldError):
            self.engine.populate(self.record, self.template_def)

    def test_extra_hr_fields_ignored(self):
        # 'location' and 'start_date' are in the record but not the template body.
        # This should succeed silently without altering the document.
        doc = self.engine.populate(self.record, self.template_def)
        self.assertNotIn("London", doc.body)