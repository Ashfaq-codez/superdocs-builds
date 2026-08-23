from backend.models.domain import AssembledDocument


class SuperDocsAdapter:
    """Translates a structured AssembledDocument into a precise SuperDocs instruction payload."""

    def format_instruction(self, document: AssembledDocument) -> str:
        if not document.sections:
            return ""

        formatted_sections = []

        for section in document.sections:
            section_parts = []

            # 1. Handle explicit page breaks
            if section.page_break_before:
                section_parts.append("[PAGE BREAK]")

            # 2. Inject the semantic title
            if section.title:
                section_parts.append(f"# {section.title}")

            # 3. Append verbatim paragraphs
            if section.paragraphs:
                section_parts.extend(section.paragraphs)

            # Join the elements of this specific section with double newlines
            formatted_section = "\n\n".join(section_parts)
            formatted_sections.append(formatted_section)

        # Join completely separate sections with a horizontal rule marker
        return "\n\n---\n\n".join(formatted_sections)