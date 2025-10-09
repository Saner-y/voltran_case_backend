from .database import SessionLocal
from sqlalchemy.orm import Session
from .models import Job

def create_job(db: Session, job_id: str, prompt: str, filename: str):
    j = Job(
        id=job_id,
        prompt=prompt,
        status="pending",
        # created_at modelde default olduğu için burada tekrar belirtmeye gerek yok
        original_filename=filename
    )
    db.add(j)
    db.commit()
    db.refresh(j)
    return j

def get_job(db: Session, job_id: str):
    return db.query(Job).filter(Job.id == job_id).first()

def update_job(db: Session, job_id: str, **kwargs):
    j = db.query(Job).filter(Job.id == job_id).first()
    if not j:
        return None
    for k, v in kwargs.items():
        setattr(j, k, v)
    db.commit()
    db.refresh(j)
    return j



def list_jobs(limit: int = 50):
    db = SessionLocal()
    rows = db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()
    db.close()
    return rows
