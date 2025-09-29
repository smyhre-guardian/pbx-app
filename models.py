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

class PortStatus(SQLModel, table=False):
    extension: str = Field(description="Extension number")
    port_name: str = Field(description="Port name")
    status: str = Field(description="Current status of the port")
    last_update: datetime = Field(description="Last status update time")

class PhoneNumber(PhoneNumberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Read-only CDR model mapping
class CdrBase(SQLModel):
    """Base (non-table) model for CDR rows. This is intended for read-only access.

    Note: many CDR columns in older MySQL/Asterisk setups use '' or '0000-00-00 00:00:00'
    as defaults which don't map cleanly to Python types; fields that may be empty or
    use zero-dates are represented as Optional where appropriate to avoid parsing
    errors when reading legacy rows.
    """
    calldate: Optional[datetime] = Field(default=None)
    clid: str = Field(default='', max_length=80)
    src: str = Field(default='', max_length=80)
    dst: str = Field(default='', max_length=80)
    dcontext: str = Field(default='', max_length=80)
    channel: str = Field(default='', max_length=80)
    dstchannel: str = Field(default='', max_length=80)
    lastapp: str = Field(default='', max_length=80)
    lastdata: Optional[str] = Field(default=None, max_length=1024)
    duration: int = Field(default=0)
    billsec: int = Field(default=0)
    disposition: str = Field(default='', max_length=45)
    amaflags: int = Field(default=0)
    accountcode: str = Field(default='', max_length=20)
    userfield: str = Field(default='', max_length=255)
    uniqueid: str = Field(default='', max_length=32)

    orig_dnis: Optional[str] = Field(default=None, max_length=15)


class Cdr(CdrBase, table=True):
    __tablename__ = "vCDR"
    __table_args__ = {'schema': 'DW_Staging.dbo'}
    id: Optional[int] = Field(default=None, primary_key=True)


# Lumen table model
class Lumen(SQLModel, table=True):
    __tablename__ = "lumen"
    __table_args__ = {'schema': 'phones'}
    id: int = Field(default=None, primary_key=True)
    TN: Optional[int] = Field(default=None, index=True)
    ring_to: Optional[str] = Field(default=None)
    DNIS: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    order_num: Optional[str] = Field(default=None)
    port_date: Optional[str] = Field(default=None)
    usage: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None)

class LumenDw(SQLModel, table=True):
    __tablename__ = "lumen"
    __table_args__ = {'schema': 'DW_Staging.pbx'}
    id: int = Field(default=None, primary_key=True)
    TN: Optional[int] = Field(default=None, index=True)
    ring_to: Optional[str] = Field(default=None)
    DNIS: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    order_num: Optional[str] = Field(default=None)
    port_date: Optional[str] = Field(default=None)
    usage: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None)


# Model for DW view vPhoneLookup
class vPhoneLookup(SQLModel, table=False):
    cs_no: str
    cnt: int
    phone: str
    first_day: Optional[int] = None
    last_day: Optional[int] = None
    row_count: Optional[int] = None


