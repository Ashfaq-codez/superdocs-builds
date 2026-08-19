import re

from backend.core.exceptions import ClauseFormatError, EmptyAssemblyError
from backend.models.domain import AssembledDocument, AssembledSection, ClauseDefinition


class AssemblyEngine:
    """Deterministic document assembly engine."""

    def assemble(self, clauses: list[ClauseDefinition]) -> AssembledDocument:
        if not clauses:
            raise EmptyAssemblyError("Cannot assemble an empty list of clauses.")

        sections = []
        for clause in clauses:
            # 1. Normalize Title & Body
            title = clause.title.strip() if clause.title else ""
            body = clause.body.strip() if clause.body else ""

            # 2. Enforce Format Integrity
            if not title and not body:
                raise ClauseFormatError(f"Clause '{clause.id}' has both an empty title and an empty body.")

            # 3. Paragraph Boundary Splitting
            paragraphs = []
            if body:
                # Normalize carriage returns and split on blank lines (1 or more blank lines between text)
                normalized_body = body.replace("\r\n", "\n")
                raw_paras = re.split(r'\n\s*\n', normalized_body)
                
                for p in raw_paras:
                    cleaned_p = p.strip()
                    if cleaned_p:
                        paragraphs.append(cleaned_p)

            # 4. Construct Structured Representation
            sections.append(AssembledSection(
                source_clause_id=clause.id,
                title=title,
                paragraphs=paragraphs,
                page_break_before=clause.formatting_hints.page_break_before
            ))

        return AssembledDocument(sections=sections)