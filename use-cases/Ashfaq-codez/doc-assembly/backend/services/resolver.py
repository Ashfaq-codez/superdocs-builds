import json
from pathlib import Path
from pydantic import ValidationError

from backend.core.exceptions import (
    ClauseNotFoundError,
    InvalidRequestError,
    LibraryConfigurationError,
)
from backend.models.domain import ClauseDefinition


class ClauseResolver:
    """Deterministic resolver that maps clause identifiers to domain models via registry.json."""

    def __init__(self, library_base_path: str | Path):
        self.library_base_path = Path(library_base_path).resolve()
        self.registry_path = self.library_base_path / "registry.json"
        
        if not self.registry_path.exists():
            raise LibraryConfigurationError(f"Registry not found at {self.registry_path}")
        
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
        except Exception as exc:
            raise LibraryConfigurationError(f"Failed to load registry.json: {exc}") from exc

    def resolve(self, clause_ids: list[str]) -> list[ClauseDefinition]:
        if not clause_ids:
            raise InvalidRequestError("The list of requested clause IDs cannot be empty.")
            
        # 1. Validate inputs (Blank IDs only, duplicates are natively supported)
        for cid in clause_ids:
            if not cid or not cid.strip():
                raise InvalidRequestError("Requested clause IDs cannot be blank.")

        results = []
        
        # 2. Resolve clauses preserving exact requested order (including duplicates)
        for cid in clause_ids:
            if cid not in self.registry:
                raise ClauseNotFoundError(f"Clause '{cid}' not found in registry.")
                
            relative_path_str = self.registry[cid]
            target_path = (self.library_base_path / relative_path_str).resolve()
            
            # Path Traversal Protection
            try:
                target_path.relative_to(self.library_base_path)
            except ValueError as exc:
                raise LibraryConfigurationError(f"Path traversal detected for clause '{cid}'") from exc

            if not target_path.exists() or not target_path.is_file():
                raise LibraryConfigurationError(f"File missing for clause '{cid}' at {target_path}")

            # 3. Parse and Validate Domain Model
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    clause_data = json.load(f)
                clause_def = ClauseDefinition.model_validate(clause_data)
                results.append(clause_def)
            except json.JSONDecodeError as exc:
                raise LibraryConfigurationError(f"Malformed JSON in clause '{cid}'") from exc
            except ValidationError as exc:
                raise LibraryConfigurationError(f"Invalid ClauseDefinition data for '{cid}'") from exc
            except Exception as exc:
                raise LibraryConfigurationError(f"Unexpected error loading clause '{cid}'") from exc
                
        return results