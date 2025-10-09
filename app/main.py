import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import engine, Base, get_db
from . import crud
from .schemas import JobOut
from .falai_client import generate_image_from_bytes

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Image Editing Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Background task ---
async def process_job(job_id: str, image_bytes: bytes, prompt_text: str, db: Session):
    try:
        print(f"🚀 Processing job {job_id} with prompt: {prompt_text}")
        crud.update_job(db, job_id, status="processing")

        resp = await generate_image_from_bytes(image_bytes, prompt_text)

        result_url = (
            resp.get("images", [{}])[0].get("url") if isinstance(resp.get("images"), list) else None
        )

        if result_url:
            print(f"✅ Image generated: {result_url}")
            crud.update_job(db, job_id, status="done", result_url=result_url)
        else:
            print("⚠️ Fal.ai response has no result_url.")
            crud.update_job(db, job_id, status="failed")

    except Exception as e:
        import traceback
        print("❌ Exception in process_job:", e)
        traceback.print_exc()
        crud.update_job(db, job_id, status="failed")


# --- Endpoints ---
@app.post("/api/jobs", response_model=JobOut)
async def create_job(
        background_tasks: BackgroundTasks,
        prompt: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    image_bytes = await file.read()  # Resmi byte olarak oku
    job_id = str(uuid.uuid4())

    db_job = crud.create_job(db, job_id, prompt, file.filename)

    # Arka plan görevine dosyanın yolunu değil, byte'larını yolluyoruz
    background_tasks.add_task(process_job, job_id, image_bytes, prompt, db)

    return JobOut.from_orm(db_job)

@app.get("/api/jobs/{job_id}", response_model=JobOut)
def get_job_endpoint(job_id: str, db: Session = Depends(get_db)): # Endpoint adını değiştirdim
    j = crud.get_job(db, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut.from_orm(j)


@app.get("/api/jobs", response_model=list[JobOut])
def list_jobs(limit: int = 50):
    rows = crud.list_jobs(limit=limit)
    return [JobOut.from_orm(r) for r in rows]
