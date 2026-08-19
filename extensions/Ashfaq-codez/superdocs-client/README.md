# SuperDocs Client (Shared SDK)

This project provides a reusable integration foundation for building applications on top of the SuperDocs platform. It exists to decouple application business logic (such as HR composers or document assembly services) from the underlying SuperDocs transport mechanics (REST/MCP).

The minimum contract with SuperDocs involves four operations: upload a document, send an edit instruction, approve the proposed changes, and export the finished file. This SDK exposes these four abstract capabilities:
1. `upload`
2. `propose_edit`
3. `approve_edit`
4. `export`

### Current State: Mock Adapter
The current implementation utilizes a `MockSuperDocsClient`. A live HTTP/MCP adapter is intentionally deferred until the concrete SuperDocs API schemas (authentication, payloads, polling mechanisms) are verified. The mock client simulates the domain workflow offline using deterministic state and synthetic IDs, but does NOT pretend to implement the actual SuperDocs API infrastructure (e.g., S3 pre-signed URLs).

### Running Tests
To run the test suite ensuring the mock honors the domain contract:
```bash
python -m unittest discover -s tests