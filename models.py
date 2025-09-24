from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import field_validator
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


# Shared validation helpers
def _validate_number_value(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError("number must be a string of 10 digits")
    s = v.strip()
    if not s.isdigit() or len(s) != 10:
        raise ValueError("number must contain exactly 10 digits")
    return s


def _validate_point_to_value(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("point_to must be a string of 4-10 digits")
    s = v.strip()
    if not s.isdigit() or len(s) > 10 or len(s) < 4:
        raise ValueError("point_to must contain 4-10 digits")
    return s

class PhoneNumberBase(SQLModel):
    number: str = Field(index=True, unique=True, max_length=16)
    point_to: Optional[str] = Field(default=None, index=True, max_length=10)
    label: Optional[str] = Field(default=None, index=True, max_length=128)
    usage: Optional[str] = Field(default=None, index=True, max_length=64)
    path: Optional[str] = Field(default=None, max_length=1024)

    @field_validator("number")
    def validate_number(cls, v: str) -> str:
        return _validate_number_value(v)
    
    @field_validator("point_to")
    def validate_point_to(cls, v: Optional[str]) -> Optional[str]:
        return _validate_point_to_value(v)

class PhoneNumberCreate(PhoneNumberBase):
    pass


class PhoneNumberUpdate(PhoneNumberBase):
    pass

class PhoneNumber(PhoneNumberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

