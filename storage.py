from http.client import HTTPException
import sys
from time import sleep
from typing import Optional, List, Any, Union, cast
import os
from collections import defaultdict
from sqlmodel import SQLModel, Session, select, create_engine, col
from models import LumenDw, PhoneNumber, Lumen, Cdr, vPhoneLookup, PortStatus
from datetime import date, datetime
from sqlalchemy import desc, text
from sqlalchemy.engine import URL

def _build_mssql_url_from_env(prefix: str = "") -> Union[str,URL]:
    # prefix allows APP_ or CDR_ env vars; default to no prefix
    print ("Building MSSQL URL from env with prefix: " + prefix)
    server = os.getenv(f"{prefix}DB_SERVER", "nwa10")
    database = os.getenv(f"{prefix}DB_NAME", "DashboardTest")
    driver = os.getenv(f"{prefix}ODBC_DRIVER", "ODBC Driver 18 for SQL Server")
    username = os.getenv(f"{prefix}DB_USER", "")
    password = os.getenv(f"{prefix}DB_PASSWORD", "")
    query = {
        "driver": driver,
        "TrustServerCertificate": "yes",
        "Encrypt": "yes"
    }
    if ( username == "" ):
        query["Trusted_Connection"] = "yes"
    else:
        query["authentication"] = "SqlPassword"
        query["UID"] = username
        query["PWD"] = password
    connection_string = URL.create(
        "mssql+pyodbc",
        host=server,
        port=1433,
        database=database,
        query=query,
    )
    print (connection_string)
    return connection_string

def _build_mysql_url_from_env(prefix: str = "") -> Union[str,URL]:
    server = os.getenv(f"{prefix}DB_SERVER", "127.0.0.1")
    print ("server: " + server)
    port = os.getenv(f"{prefix}DB_PORT", "")
    database = os.getenv(f"{prefix}DB_NAME", "phones")
    user = os.getenv(f"{prefix}DB_USER", "root")
    password = os.getenv(f"{prefix}DB_PASSWORD", "badpass").strip()
    driver = os.getenv(f"{prefix}DB_DRIVER", "pyodbc")
    query = {"charset": os.getenv(f"{prefix}DB_CHARSET", "utf8mb4")}
    # driver = 'mariadbconnector'
    if driver == "pyodbc":
        return str(f"mysql+pyodbc://{user}:{password}@{server}")
    connection_string = URL.create(
        f"mysql+{driver}",
        username=user or None,
        password=password or None,
        host=server,
        port=int(port) if port else None,
        database=database,
        # query=query,
    )
    # print(str(connection_string))
    return connection_string


def get_database_url(role: str = "app") -> Union[str,URL]:
    """Return a database URL for the given role.

    Priority:
      - If DATABASE_URL is set, return it (useful for tests)
      - Else, use role-specific env vars (APP_* for app, CDR_* for cdr)
      - Defaults: app -> mssql, cdr -> mysql
    """
    env = os.getenv("DATABASE_URL")
    if env:
        return env

    role = (role or "app").lower()
    if role == "cdr":
        db_type = os.getenv("CDR_DB_TYPE", "mysql").lower()
        if db_type == "mysql":
            return _build_mysql_url_from_env("CDR_")
        # fallback to mssql if requested
        return _build_mssql_url_from_env("CDR_")

    if role == "dw":
        return _build_mssql_url_from_env("DW_")

    # app role (default)
    db_type = os.getenv("APP_DB_TYPE", "mssql").lower()
    if db_type == "mysql":
        return _build_mysql_url_from_env("APP_")
    return _build_mssql_url_from_env("APP_")


# Engines for each role
DATABASE_URL_APP = get_database_url("app")
DATABASE_URL_CDR = get_database_url("cdr")
DATABASE_URL_DW = get_database_url("dw")
engine_app = create_engine(DATABASE_URL_APP, echo=False)
engine_cdr = create_engine(DATABASE_URL_CDR, echo=False)
engine_dw = create_engine(DATABASE_URL_DW, echo=False)

def create_db_and_tables_app():
    SQLModel.metadata.create_all(engine_app)



# def create_db_and_tables():
    # backward compatible alias used by main/tests: create app DB tables
    # return create_db_and_tables_app()


class DwStorage:

    def lookup_phone(self, number: str) -> Optional[vPhoneLookup]:
        with engine_dw.connect() as conn:
            result = conn.execute(text("SELECT cs_no, cnt, phone, first_day, last_day FROM vPhoneLookup WHERE phone = :phone ORDER BY cnt desc, last_day desc"), {"phone": number})
            rows = result.fetchall()
            if rows:
                row = rows[0]
                obj = vPhoneLookup(cs_no=row[0], cnt=row[1], phone=row[2], first_day=row[3], last_day=row[4], row_count=len(rows))
                return obj
            return None

class AppStorage:
    # def __init__(self):
        # create_db_and_tables_app()

    def add(self, number: str, point_to: Optional[str] = None) -> Optional[PhoneNumber]:
        norm = "".join(ch for ch in number if ch.isdigit())
        with Session(engine_app) as session:
            existing = session.exec(select(PhoneNumber).where(PhoneNumber.number == norm)).first()
            if existing:
                return None
            obj = PhoneNumber(number=norm, point_to=point_to)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def list_all(self) -> List[PhoneNumber]:
        with Session(engine_app) as session:
            stmt = select(PhoneNumber)
            return list(session.exec(stmt))

    def get(self, item_id: int) -> Optional[PhoneNumber]:
        with Session(engine_app) as session:
            return session.get(PhoneNumber, item_id)

    def delete(self, item_id: int) -> bool:
        with Session(engine_app) as session:
            obj = session.get(PhoneNumber, item_id)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True

    def update(self, item_id: int, **fields) -> Optional[PhoneNumber]:
        with Session(engine_app) as session:
            obj = session.get(PhoneNumber, item_id)
            if not obj:
                return None
            if "number" in fields and fields["number"] is not None:
                norm = "".join(ch for ch in fields["number"] if ch.isdigit())
                existing = session.exec(
                    select(PhoneNumber).where(PhoneNumber.number == norm, PhoneNumber.id != item_id)
                ).first()
                if existing:
                    return None
                obj.number = norm
            for k in ("point_to", "label", "usage", "path"):
                if k in fields:
                    setattr(obj, k, fields[k])
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj



class CdrStorage:
    """Read-only storage class for CDRs. Provides CDR queries and join to Lumen."""
    def __init__(self):
        pass

    def list_with_lumen_join(self, start: Optional[datetime] = None, end: Optional[datetime] = None, limit: int = 100, q: Optional[str] = None) -> list:
        """Return CDRs joined with Lumen on orig_dnis == TN, including Lumen fields."""
        with Session(engine_dw) as session:
            col = cast(Any, Cdr.calldate)
            stmt = select(Cdr, LumenDw).join(LumenDw, Cdr.__table__.c.orig_dnis == LumenDw.__table__.c.TN) # type: ignore
            if start and end:
                stmt = stmt.where(col != None, col >= start, col <= end)
            if q:
                ql = str(q).lower()
                stmt = stmt.where(
                    (Cdr.__table__.c.src.like(f"%{ql}%")) | # type: ignore
                    (Cdr.__table__.c.dst.like(f"%{ql}%")) | # type: ignore
                    (Cdr.__table__.c.clid.like(f"%{ql}%")) | # type: ignore
                    (Cdr.__table__.c.orig_dnis.like(f"%{ql}%")) # type: ignore
                )
            stmt = stmt.order_by(desc(col)).limit(limit)
            results = session.exec(stmt).all()
            out = []
            for cdr, lumen in results:
                calldate = getattr(cdr, "calldate", None)
                num = str(getattr(cdr, "src", None))[-10:]
                # print (f"num: {num}")
                lookup = DwStorage().lookup_phone(num)
                out.append({
                    "id": cdr.id,
                    "pbx": getattr(cdr, "PBX", None),
                    "caller": getattr(cdr, "src", None),
                    "callee": getattr(cdr, "dst", None),
                    "calldate": calldate.isoformat() if calldate else None,
                    "orig_dnis": getattr(cdr, "orig_dnis", None),
                    "duration": getattr(cdr, "duration", None),
                    "disposition": getattr(cdr, "disposition", None),
                    # dw fields
                    "cs_no": getattr(lookup, "cs_no", None) if lookup else None,
                    "cs_no_rows": lookup.row_count if lookup else None,
                    # Lumen fields
                    "lumen_TN": getattr(lumen, "TN", None),
                    "lumen_ring_to": getattr(lumen, "ring_to", None),
                    "lumen_DNIS": getattr(lumen, "DNIS", None),
                    "lumen_status": getattr(lumen, "status", None),
                    "lumen_order_num": getattr(lumen, "order_num", None),
                    "lumen_port_date": getattr(lumen, "port_date", None),
                    "lumen_usage": getattr(lumen, "usage", None),
                    "lumen_notes": getattr(lumen, "notes", None),
                    "lumen_company": getattr(lumen, "company", None),
                })
            return out

    def list_all_lumen(self) -> List[Lumen]:
        with Session(engine_cdr) as session:
            stmt = select(Lumen)
            return list(session.exec(stmt))

    def list_recent(self, limit: int = 100) -> List[Cdr]:
        with Session(engine_cdr) as session:
            col = cast(Any, Cdr.calldate)
            stmt = select(Cdr).order_by(desc(col)).limit(limit)
            return list(session.exec(stmt))

    def list_all(self) -> List[Cdr]:
        with Session(engine_cdr) as session:
            stmt = select(Cdr)
            return list(session.exec(stmt))

    def get(self, item_id: int) -> Optional[Cdr]:
        with Session(engine_cdr) as session:
            return session.get(Cdr, item_id)

    def list_by_date_range(self, start: datetime, end: datetime, limit: Optional[int] = None) -> List[Cdr]:
        with Session(engine_cdr) as session:
            col = cast(Any, Cdr.calldate)
            stmt = select(Cdr).where(col != None, col >= start, col <= end).order_by(desc(col))
            if limit:
                stmt = stmt.limit(limit)
            return list(session.exec(stmt))


# Port Status Storage
class PortStatusStorage:
    def list_all(self):
        with Session(engine_dw) as session:
            query = text("""
                SELECT *
                FROM vPortStatus
                ORDER BY TN
            """)
            result = session.execute(query)
            return [dict(row._mapping) for row in result]

    def update(self, tn: str, fields: dict):
        # Trim all string fields before updating
        trimmed_fields = {key: value.strip() if isinstance(value, str) else value for key, value in fields.items()}
        with Session(engine_cdr) as session:
            query = text("UPDATE lumen SET " + ", ".join([f"`{key}` = :{key}" for key in trimmed_fields.keys()]) + " WHERE TN = :tn")
            params = {**trimmed_fields, "tn": tn}
            result = session.execute(query, params)
            session.commit()
            return True
        
    def get_rcvr_prefixes(self, prefix):
        with Session(engine_dw) as session:
            query = text("SELECT * FROM vRcvrPrefix WHERE replacement = :prefix")
            params = {"prefix": prefix}
            result = session.execute(query, params)
            prefixes = [dict(row._mapping) for row in result]
            return prefixes;
    def get_asterisk_extensions(self):
        with Session(engine_dw) as session:
            query = text("SELECT * from vAsteriskExtensions")
            result = session.execute(query)
            extensions = [dict(row._mapping) for row in result]
            return extensions;

def get_pbx_diff(pbx: str) -> Optional[list[dict]]:
    """Return a diff of the current dialplan for the specified PBX compared to the last saved version."""
    s = PortStatusStorage()
    current = s.get_asterisk_extensions()

    etc_dir = os.getenv("ASTERISK_ETC_DIR", "/etc/asterisk/")
    if not os.path.isdir(etc_dir):
        return None
    saved_file = os.path.join(etc_dir, f"avaya_x.conf")
    if not os.path.isfile(saved_file):
        return None
    current.sort(key=lambda x: x.get("exten", ""))
    current_lines = [row["exten"] for row in current if "exten" in row]

    # assert False, current_lines
    try:
        import difflib
        from collections import defaultdict
        with open(saved_file, "r") as f_saved:
            # Map the current extensions to lines using the "exten" field
            
            saved_lines = f_saved.readlines()
            saved_lines = sorted([line.strip() for line in saved_lines if line.strip().startswith("exten") and not 'to_ivr' in line])
            current_lines = sorted([line.strip() for line in current_lines if line.strip().startswith("exten")])
            # current_lines = sorted([line.strip() for line in current_lines.splitlines() if line.strip()])

            current_dict = {line[9:19]: line[22:] for line in current_lines}
            saved_dict = {line[9:19]: line[22:] for line in saved_lines}

            all_nums = sorted(set(current_dict.keys()).union(saved_dict.keys()))

            left_out = []
            right_out = []
            out = []
            for key in all_nums:
                if not key.isdigit():
                    continue
                in_left = key in saved_dict;
                in_right = key in current_dict;

                is_match = in_left and in_right and (
                    saved_dict[key].strip().split(';')[0].strip()
                    == current_dict[key].strip().split(';')[0].strip()
                )
                out.append({
                    "phn": key,
                    "left": saved_dict.get(key, f"MISSING in old"),
                    "right": current_dict.get(key, f"MISSING in new"),
                    "left_full": saved_dict.get(key, ""),
                    "right_full": current_dict.get(key, ""),
                    "is_match": is_match,
                    "is_new": in_right and not in_left
                })
                if key in saved_dict:
                    left_out.append(saved_dict[key])
                else:
                    left_out.append(f"exten => {key},MISSING exten {key} in old")
                if key in current_dict:
                    right_out.append(current_dict[key])
                else:
                    right_out.append(f"exten => {key},MISSING exten {key} in new")
                    
            saved_txt = "\n".join(left_out)
            current_txt = "\n".join(right_out)

            # with open(r"C:\\Temp\\saved.conf", "w", encoding="utf-8") as f:
                # f.write(saved_txt)

            # with open(r"C:\\Temp\\current.conf", "w", encoding="utf-8") as f:
                # f.write(current_txt)

            return out

            d = difflib.Differ()
            return "\n".join(d.compare(left_out, right_out))

            diff = difflib.unified_diff(
                left_out,
                right_out,
                fromfile=f"saved/{pbx}_extensions.conf",
                tofile=f"current/{pbx}_extensions.conf",
                lineterm="\n"
            )
            diff_text = "\n".join(diff)
            return diff_text if diff_text else None
    except Exception as e:
        print(f"Error generating diff:  {type(e).__name__} {e}", file=sys.stderr)
        return None

def sync_pbx_extensions(pbx: str) -> bool|str:
    """Save the current dialplan for the specified PBX to the saved version file."""
    s = PortStatusStorage()
    current = s.get_asterisk_extensions()

    etc_dir = os.getenv("ASTERISK_ETC_DIR", "/etc/asterisk/")
    if not os.path.isdir(etc_dir):
        return False
    saved_file = os.path.join(etc_dir, f"avaya_x.conf.pending")
    current.sort(key=lambda x: (x.get("order_num", ""), x.get("TN", "")))
    # Group extensions by order_num and add a header for each group
    current_lines = ["[avaya_x]\n"]
    current_lines.append("exten => 2066265871,1,Goto(to_ivr,${EXTEN:-10}, 1)") # IVR ext
    current_group = None
    for row in current:
        group = row.get("order_num", "")
        if group != current_group:
            current_group = group
            port_date = row.get("port_date", "")
            current_lines.append(f"\n\n; ---- Order Number: {group}  Port Date: {port_date} ----\n")
        exten = row.get("exten", "")
        if exten:
            current_lines.append(exten)

    current_lines.append("; Default fallthrough - send all to avaya")
    current_lines.append("exten => _X.,1,Goto(to_avaya,${EXTEN:-10},1)")
    try:
        with open(saved_file, "w", encoding="utf-8") as f:
            f.write("\n".join(current_lines) + "\n")
        
        import subprocess
        try:
            result = subprocess.run(["sudo", "/home/guardian/pbx-app/syncPbx.sh", pbx], capture_output=True, text=True, check=True)
            return result.stdout or result.stderr or True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"sync failed: {e.stderr}")
        
    except Exception as e:
        raise RuntimeError(f"Error saving PBX extensions: {type(e).__name__} {e}")
        return False

def excel_diff(data: list[dict]) -> list[dict]:
    """Compare uploaded Excel data with existing Lumen data and return differences."""
    s = CdrStorage()
    existing = s.list_all_lumen()
    existing_dict = {str(row.TN): row for row in existing}
    column_map = {
        "Toll Free/TN's": "TN",
        "Ring-To #": "ring_to",
        "DNIS": "DNIS",
        "Port Status": "status",
        "Order Number": "order_num",
        "Port Date": "port_date",
        "Usage": "usage",
        "Notes": "notes",
    }

    import dateutil.parser
    def safe_parse_date(val):
        if not val or str(val).strip().lower() in ("none", "nat"):
            return "None"
        try:
            return dateutil.parser.parse(val).strftime("%Y-%m-%d")
        except Exception:
            return "None"
    diffs = []
    for row in data:
        tn = str(row.get("Toll Free/TN's", "")).strip()
        if not tn:
            continue
        if tn in existing_dict:
            existing_row = existing_dict[tn]
            row_diff = {
                "TN": tn,
                "is_new": False,
                "differences": {},
                "existing": {k: str(getattr(existing_row, k, "")) for k in column_map.values()}
            }
            for key, col in column_map.items():
                new_value = str(row.get(key, "")).strip()
                existing_value = str(getattr(existing_row, col, "")).strip()
                if col == "port_date":
                    existing_value = safe_parse_date(existing_value)
                    new_value = safe_parse_date(new_value)
                if new_value != existing_value:
                    if col == "ring_to" and new_value[-7:] == existing_value[-7:]:
                        continue  # ignore differences in ring_to if they only differ by area code
                    row_diff["differences"][col] = {
                        "old": existing_value,
                        "new": new_value
                    }
            if row_diff["differences"]:
                diffs.append(row_diff)
        else:
            diffs.append({
                "TN": tn,
                "is_new": True,
                "differences": row,
                "existing": None
            })
    return diffs

# Instances
storage_instance = AppStorage()  # backward-compatible name used across the codebase
app_storage = storage_instance
cdr_storage = CdrStorage()
port_status_storage = PortStatusStorage()



