from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.app.core.database import get_db, SessionLocal # Import SessionLocal for background tasks
from db.app.db.schema.user import UserOutput
from db.app.db.schema.user_file import UserFileCreate
from db.app.service.userService import UserService
from db.app.util.init_db import create_tables
from db.app.routers.auth import authrouter
from db.app.util.protectRoute import get_current_user
from main import process_pdf, progress_store # Import progress store
from pathlib import Path
import shutil
import uuid
from sqlalchemy.orm import Session
from db.app.routers.user_file import router as user_file_router 

@asynccontextmanager
async def lifespan(app : FastAPI):
    #db initialization
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=authrouter, tags=["auth"], prefix="/auth")
app.include_router(user_file_router)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")

@app.get("/protected")
def read_protected(user : UserOutput = Depends(get_current_user)):
    return {"data": user}

def cleanup_files(*paths: Path):
    for path in paths:
        try:
            path.unlink(missing_ok=True)
            print(f"[CLEANUP] Deleted: {path.name}")
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

# --- BACKGROUND TASK WRAPPER ---
def background_task_wrapper(file_path: Path, task_id: str, user_id: int, original_filename: str):
    """
    Runs the heavy PDF processing and saves the result to DB.
    Since this runs in background, we need a fresh DB session.
    """
    try:
        # Run the heavy processing
        output_file, charts_json = process_pdf(file_path, task_id=task_id)

        if output_file and output_file.exists():
            # Create a new DB session manually
            db = SessionLocal()
            try:
                # Construct path compatible with the download endpoint
                # Format: uploads/{user_id}/{filename}
                download_link = f"uploads/{user_id}/{output_file.name}"
                
                service = UserService(session=db)
                file_data = UserFileCreate(
                    filename = original_filename,
                    download_path = download_link, 
                    json_charts = charts_json
                )
                service.add_user_file(user_id=user_id, file_data=file_data)
                
                # Update progress store with final result and URL for frontend
                if task_id in progress_store:
                    progress_store[task_id]["result"] = charts_json
                    progress_store[task_id]["download_url"] = f"/download/{user_id}/{output_file.name}"
                    
            except Exception as db_err:
                print(f"DB Error in background task: {db_err}")
                if task_id in progress_store:
                     progress_store[task_id]["status"] = f"Database Error: {str(db_err)}"
            finally:
                db.close()
        else:
             if task_id in progress_store:
                progress_store[task_id]["status"] = "Processing Failed (No Output)"

    except Exception as e:
        print(f"Critical Error in background task: {e}")

# --- START PROCESSING (Async) ---
@app.post("/process-pdf/start")
async def start_processing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db : Session = Depends(get_db),
    user: UserOutput = Depends(get_current_user)
    ):

    # 1. Setup user directory
    user_dir = UPLOAD_DIR / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # 2. Save uploaded file
    file_ext = Path(file.filename).suffix
    unique_id = uuid.uuid4().hex
    file_path = user_dir / f"{unique_id}{file_ext}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Initialize Progress
    task_id = unique_id
    progress_store[task_id] = {"status": "Queued", "percent": 0}

    # 4. Add to Background Tasks
    background_tasks.add_task(
        background_task_wrapper, 
        file_path, 
        task_id, 
        user.id, 
        file.filename
    )

    # 5. Return Task ID immediately
    return {"task_id": task_id}

# --- CHECK STATUS (Polling Endpoint) ---
@app.get("/process-pdf/status/{task_id}")
def get_status(task_id: str):
    # Return status or default error if not found
    return progress_store.get(task_id, {"status": "Not Found", "percent": 0})

# --- DOWNLOAD ENDPOINT (Updated for User Subdirectories) ---
# --- DOWNLOAD ENDPOINT (Updated for User Subdirectories) ---
# --- DOWNLOAD ENDPOINT (Updated for User Subdirectories) ---
@app.get("/download/{user_id}/{file_name}")
async def download_file(user_id: str, file_name: str):
    # First, check the new user-specific folder
    file_path = UPLOAD_DIR / user_id / file_name
    
    # Backward compatibility: If not found, check the root uploads folder for old history files
    if not file_path.exists():
        file_path = UPLOAD_DIR / file_name

    if file_path.exists():
        return FileResponse(
             path=file_path,
             filename=file_name,
             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")