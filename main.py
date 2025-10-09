from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from fastapi.responses import PlainTextResponse
from models import PhoneNumber, PhoneNumberCreate, PhoneNumberUpdate
from storage import storage_instance, cdr_storage, port_status_storage
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import HTTPException, Body
from dotenv import load_dotenv
import pandas as pd
from fastapi import UploadFile, File

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ensure tables exist (no-op if already created)
    # create_db_and_tables()
    yield
    #after shutdown tasks

app = FastAPI(title="Phone List API", version="0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Service status")
def read_root():
    return {"message": "Phone List API"}

@app.get("/git-pull", summary="Pull latest code from git")
def git_pull():
    import subprocess
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Git pull failed: {e.stderr}")

@app.post("/phone_numbers", response_model=PhoneNumber, status_code=201)
def create_phone(payload: PhoneNumberCreate):
    """Add a phone number. Validation: exactly 10 digits after removing formatting. Returns 409 if the normalized number already exists."""
    # Strip non-digits, validate 10 digits
    digits = "".join(ch for ch in payload.number if ch.isdigit())
    if len(digits) != 10:
        raise HTTPException(status_code=400, detail="number must contain exactly 10 digits")
    created = storage_instance.add(digits, payload.point_to)
    if created is None:
        raise HTTPException(status_code=409, detail="Number already exists")
    return created


@app.get("/phone_numbers", response_model=List[PhoneNumber])
def list_phones():
    return storage_instance.list_all()

@app.get("/port_status")
def list_port_status():
    """Get the status of all ports from the phone system"""
    return port_status_storage.list_all()

@app.get("/rcvr_prefix/{prefix}")
def get_rcvr_prefixes(prefix: str):
    return port_status_storage.get_rcvr_prefixes(prefix)

@app.get("/phone_numbers/{item_id}", response_model=PhoneNumber)
def get_phone(item_id: int):
    obj = storage_instance.get(item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Not found")
    return obj



@app.patch("/phone_numbers/{item_id}", response_model=PhoneNumber)
def update_phone(item_id: int, payload: PhoneNumberUpdate):
    """Partially update a phone number. If updating number it must be 10 digits after normalization; returns 409 on duplicate."""
    data = payload.model_dump(exclude_unset=True)
    updated = storage_instance.update(item_id, **data)
    if updated is None:
        # could be not found or duplicate number
        # disambiguate: check existence
        if storage_instance.get(item_id) is None:
            raise HTTPException(status_code=404, detail="Not found")
        raise HTTPException(status_code=409, detail="Number already exists")
    return updated


@app.delete("/phone_numbers/{item_id}", status_code=204)
def delete_phone(item_id: int):
    ok = storage_instance.delete(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return None



@app.get("/call_records")
def list_call_records(
    q: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    """Return call records from the CDR database, joined with Lumen fields."""
    try:
        page = max(1, int(page))
    except Exception:
        page = 1
    try:
        page_size = max(1, min(1000, int(page_size)))
    except Exception:
        page_size = 25

    def _parse_iso(s: str) -> datetime:
        try:
            s2 = s.rstrip("Z")
            return datetime.fromisoformat(s2)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid datetime: {s}")

    start_dt = _parse_iso(start) if start else None
    end_dt = _parse_iso(end) if end else None
    rows = cdr_storage.list_with_lumen_join(
        start=start_dt,
        end=end_dt,
        limit=page * page_size,
        q=q,
    )
    start_idx = (page - 1) * page_size
    page_rows = rows[start_idx:start_idx + page_size]
    return page_rows

# DW phone lookup endpoint
@app.get("/phone_lookup")
def phone_lookup(phone: str):
    """Return all vPhoneLookup results for a given phone number from DW."""
    # Accepts phone as string, returns all matches
    results = []
    from storage import engine_dw
    from sqlalchemy import text
    with engine_dw.connect() as conn:
        query = text("SELECT cs_no, cnt, phone, first_day, last_day FROM vPhoneLookup WHERE phone = :phone ORDER BY cnt DESC, last_day DESC")
        rows = conn.execute(query, {"phone": phone}).fetchall()
        for row in rows:
            results.append({"cs_no": row[0], "cnt": row[1], "phone": row[2], "first_day": row[3], "last_day": row[4]})
    return results


@app.put("/port_status/{tn}", summary="Update port status")
def update_port_status(tn: str, payload: dict = Body(...)):
    """Update specific fields for a port status entry."""
    updated = port_status_storage.update(tn, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Port status entry not found")
    return updated

@app.get("/pbx-diff/{pbx}", summary="Diff dialplan for PBX")
def diff_pbx(pbx: str):
    """Return a diff of the current dialplan for the specified PBX compared to the last saved version."""
    from storage import get_pbx_diff
    diff = get_pbx_diff(pbx)
    if diff is None:
        raise HTTPException(status_code=404, detail="PBX not found or no previous version to compare")
    # return PlainTextResponse(diff)
    return diff;

@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload an Excel file and return its contents as JSON."""
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file.file, header=3, sheet_name='TN')
        df.fillna('', inplace=True)  # Replace NaN with empty strings
        # df.dropna()

        # Convert the DataFrame to a list of dictionaries
        data = df.to_dict(orient='records')

        # Compare with what we have in database
        from storage import excel_diff
        diff = excel_diff(data)

        return {"data": diff}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/pbx-sync/{pbx}", summary="Synchronize PBX")
def pbx_sync(pbx: str):
    """Simulate PBX synchronization logic."""
    try:
        from storage import sync_pbx_extensions
        sync_pbx_extensions(pbx)
        result = {
            "status": "success",
            "message": "PBX synchronization completed successfully."
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PBX sync failed: {str(e)}")

if __name__ == "__main__":
    # Run with: python main.py
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)