class SuperDocsError(Exception):
    """Base domain exception for all SuperDocs integration errors."""
    pass


class DocumentUploadError(SuperDocsError):
    pass


class EditProposalError(SuperDocsError):
    pass


class ApprovalError(SuperDocsError):
    pass


class ExportError(SuperDocsError):
    pass