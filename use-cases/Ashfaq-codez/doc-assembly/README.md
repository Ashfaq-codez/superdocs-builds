# Document-Assembly Microservice (Build 2)

This directory contains the Document-Assembly microservice built on top of the SuperDocs platform. It is designed to serve Legal/Finance teams and engineering units needing compliant multi-section document generation.

## Core Architecture & Workflow
- **Document Assembly from Reusable Blocks:** This service resolves an ordered list of clause identifiers into coherent documents. The `clause_library` stores reusable document clauses/sections, NOT a project source-file cache.
- **Deterministic Ordering:** The exact requested order of clause identifiers is strictly preserved. No AI or LLMs are used for clause selection or ordering.
- **SuperDocs as the Editing Layer:** The local assembly service acts as the workflow orchestrator. SuperDocs handles the actual document editing, formatting, and export layer.
- **Explicit Human Approval Gate:** There is strictly no auto-approval. Assembled documents are proposed as edits to SuperDocs and MUST pass an explicit human review gate before export operations can occur.