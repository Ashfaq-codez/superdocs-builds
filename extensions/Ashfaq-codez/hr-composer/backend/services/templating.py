import string
from backend.models.domain import HRRecord, TemplateDefinition, ComposedDocument
from backend.core.exceptions import MissingTemplateFieldError


class TemplateEngine:
    """Deterministically populates string templates based on HR records."""

    def populate(self, record: HRRecord, template_def: TemplateDefinition) -> ComposedDocument:
        record_dict = record.model_dump()
        
        # 1. Strict required field validation
        for field in template_def.required_fields:
            if field not in record_dict or not record_dict[field]:
                raise MissingTemplateFieldError(f"HR Record is missing required field: '{field}'")
                
        # 2. Deterministic substitution (No LLMs, pure string interpolation)
        template = string.Template(template_def.body_template)
        
        try:
            # .substitute() strictly fails if a $placeholder in the text has no corresponding value in the dict
            populated_body = template.substitute(record_dict)
        except KeyError as e:
            raise MissingTemplateFieldError(f"Template requires field not present in HR Record: {e}") from e

        # 3. Return object with strict provenance attached
        return ComposedDocument(
            template_id=template_def.id,
            template_version=template_def.version,
            jurisdiction=template_def.jurisdiction,
            body=populated_body
        )