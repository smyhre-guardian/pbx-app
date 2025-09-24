from typing import Optional, List
import os
from sqlmodel import SQLModel, Session, select, create_engine
from models import PhoneNumber
from sqlalchemy.engine import URL

def get_database_url() -> str:
    env = os.getenv("DATABASE_URL")
    if env:
        return env
    server = os.getenv("DB_SERVER", "nwa10")
    database = os.getenv("DB_NAME", "DashboardTest")
    driver = os.getenv("ODBC_DRIVER", "ODBC Driver 18 for SQL Server")
    connection_string = URL.create(
        "mssql+pyodbc",
        username=None,
        password=None,
        host=server,
        database=database,
        query={
            "driver": driver,
            "Trusted_Connection": "yes",
            "Encrypt": "no"
        }
    )
    return str(connection_string)


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


class Storage:
    def __init__(self):
        create_db_and_tables()

    def add(self, number: str, point_to: Optional[str] = None) -> Optional[PhoneNumber]:
        # number is expected to be digits-only (10 digits) from the API layer
        norm = "".join(ch for ch in number if ch.isdigit())
        with Session(engine) as session:
            existing = session.exec(
                select(PhoneNumber).where(PhoneNumber.number == norm)
            ).first()
            if existing:
                return None
            obj = PhoneNumber(number=norm, point_to=point_to)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def list_all(self) -> List[PhoneNumber]:
        with Session(engine) as session:
            stmt = select(PhoneNumber)
            return list(session.exec(stmt))

    def get(self, item_id: int) -> Optional[PhoneNumber]:
        with Session(engine) as session:
            return session.get(PhoneNumber, item_id)

    def delete(self, item_id: int) -> bool:
        with Session(engine) as session:
            obj = session.get(PhoneNumber, item_id)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True

    def update(self, item_id: int, **fields) -> Optional[PhoneNumber]:
        """Patch-update fields for a PhoneNumber. Returns updated object or None if not found or duplicate number."""
        with Session(engine) as session:
            obj = session.get(PhoneNumber, item_id)
            if not obj:
                return None
            # If updating number, normalize
            if 'number' in fields and fields['number'] is not None:
                norm = "".join(ch for ch in fields['number'] if ch.isdigit())
                # check for duplicates
                existing = session.exec(
                    select(PhoneNumber).where(PhoneNumber.number == norm, PhoneNumber.id != item_id)
                ).first()
                if existing:
                    return None
                obj.number = norm
            # other optional fields
            for k in ('point_to', 'label', 'usage', 'path'):
                if k in fields:
                    setattr(obj, k, fields[k])
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj


storage_instance = Storage()

