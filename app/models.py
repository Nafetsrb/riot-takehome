from __future__ import annotations
from typing import Any, Dict
from pydantic import BaseModel, Field, field_validator

class VerifyInput(BaseModel):
    """Schema for /verify endpoint: includes the signature and the data.


    Additional constraints:
    - `signature` must be a non-empty string.
    - `data` must be a JSON *object* (dict) — arrays, numbers, strings are rejected.
    """
    signature: str = Field(..., min_length=1, description='Hex-encoded signature')
    data: Dict[str, Any] = Field(..., description='JSON object to verify')

    @field_validator('signature')
    @classmethod
    def _non_empty_signature(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError('signature must be a non-empty string')
        return v
    
class SignOutput(BaseModel):
    """Schema for /sign response: returns the computed signature only."""
    signature: str

