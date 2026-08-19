from abc import ABC, abstractmethod
from typing import List

from .models import (
    ApprovalDecision,
    ApprovalResult,
    DocumentRef,
    EditProposal,
    ExportFormat,
    ExportResult,
)


class SuperDocsClientInterface(ABC):
    """Abstract asynchronous interface for SuperDocs domain capabilities."""

    @abstractmethod
    async def upload(self, file_path: str) -> DocumentRef:
        """
        Uploads a document and returns a tracking reference.
        (Note: file_path: str is a temporary internal abstraction, not a claim about the real API).
        """
        pass

    @abstractmethod
    async def propose_edit(
        self, document: DocumentRef, instruction: str
    ) -> EditProposal:
        """Submits an edit instruction for the document, generating a proposal."""
        pass

    @abstractmethod
    async def approve_edit(
        self, proposal_id: str, decision: ApprovalDecision
    ) -> ApprovalResult:
        """Gates the edit by applying a human review decision."""
        pass

    @abstractmethod
    async def export(
        self, document: DocumentRef, formats: List[ExportFormat]
    ) -> ExportResult:
        """Exports the tracked document into the requested formats."""
        pass