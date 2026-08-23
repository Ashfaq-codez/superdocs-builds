from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.api.router import router
from backend.core.exceptions import (
    UnsupportedJurisdictionError,
    MissingTemplateFieldError,
    ConfigurationError,
    ComposerNotFoundError,
    InvalidStateTransitionError,
    HRComposerError
)
from superdocs_client.exceptions import SuperDocsError

app = FastAPI(title="HR Composer Backend (Build 1)")

app.include_router(router)


@app.exception_handler(UnsupportedJurisdictionError)
async def handle_unsupported_jurisdiction(request: Request, exc: UnsupportedJurisdictionError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(MissingTemplateFieldError)
async def handle_missing_field(request: Request, exc: MissingTemplateFieldError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(ComposerNotFoundError)
async def handle_not_found(request: Request, exc: ComposerNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InvalidStateTransitionError)
async def handle_invalid_state(request: Request, exc: InvalidStateTransitionError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(ConfigurationError)
async def handle_configuration_error(request: Request, exc: ConfigurationError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(SuperDocsError)
async def handle_superdocs_error(request: Request, exc: SuperDocsError):
    return JSONResponse(status_code=502, content={"detail": f"SuperDocs SDK Error: {str(exc)}"})

@app.exception_handler(HRComposerError)
async def handle_generic_error(request: Request, exc: HRComposerError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})