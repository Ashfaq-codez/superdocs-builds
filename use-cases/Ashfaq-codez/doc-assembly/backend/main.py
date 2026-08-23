from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.api.router import router
from backend.core.exceptions import (
    AssemblyNotFoundError,
    ClauseNotFoundError,
    InvalidRequestError,
    InvalidStateTransitionError,
    DocAssemblyError
)
from superdocs_client.exceptions import SuperDocsError

app = FastAPI(
    title="Document Assembly Microservice",
    description="Orchestrates multi-section document composition and SuperDocs review workflows."
)

app.include_router(router)


# --- Exception Handlers ---

@app.exception_handler(InvalidRequestError)
async def handle_invalid_request(request: Request, exc: InvalidRequestError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(ClauseNotFoundError)
async def handle_clause_not_found(request: Request, exc: ClauseNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(AssemblyNotFoundError)
async def handle_assembly_not_found(request: Request, exc: AssemblyNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InvalidStateTransitionError)
async def handle_invalid_state(request: Request, exc: InvalidStateTransitionError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(SuperDocsError)
async def handle_superdocs_error(request: Request, exc: SuperDocsError):
    return JSONResponse(status_code=502, content={"detail": f"Upstream SuperDocs error: {str(exc)}"})

@app.exception_handler(DocAssemblyError)
async def handle_generic_domain_error(request: Request, exc: DocAssemblyError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})