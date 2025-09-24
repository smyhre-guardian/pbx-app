from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import PhoneNumber, PhoneNumberCreate, PhoneNumberUpdate
from storage import storage_instance, create_db_and_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ensure tables exist (no-op if already created)
    create_db_and_tables()
    yield

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


if __name__ == "__main__":
    # Run with: python main.py
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)