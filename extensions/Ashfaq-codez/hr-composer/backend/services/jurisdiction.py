from backend.models.domain import Jurisdiction
from backend.core.exceptions import UnsupportedJurisdictionError


class JurisdictionEngine:
    """Strictly maps location strings to domain Jurisdictions without fuzzy guessing."""
    
    LOCATION_MAP = {
        "SAN FRANCISCO, CA": Jurisdiction.CALIFORNIA,
        "LOS ANGELES, CA": Jurisdiction.CALIFORNIA,
        "LONDON": Jurisdiction.UK,
        "MANCHESTER": Jurisdiction.UK,
        "NEW YORK, NY": Jurisdiction.STANDARD,
        "REMOTE - US": Jurisdiction.STANDARD
    }

    def resolve(self, location: str) -> Jurisdiction:
        if not location:
            raise UnsupportedJurisdictionError("Location cannot be empty.")
            
        standardized = location.strip().upper()
        if standardized not in self.LOCATION_MAP:
            raise UnsupportedJurisdictionError(f"Unsupported location: '{location}'")
            
        return self.LOCATION_MAP[standardized]