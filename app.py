from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.app.core.database import get_db
from db.app.db.schema.user import UserOutput
from db.app.db.schema.user_file import UserFileCreate
from db.app.service.userService import UserService
from db.app.util.init_db import create_tables
from db.app.routers.auth import authrouter
from db.app.util.protectRoute import get_current_user
from main import process_pdf
from pathlib import Path
import shutil
import uuid
from sqlalchemy.orm import Session


from db.app.routers.user_file import router as user_file_router #pne edth kalayanam


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
#test
app.include_router(user_file_router) # remove this

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="web", html=True), name="static") # y this still here idk?

@app.get("/protected") # Use for role-based access (Admin / User)  get user data like this for future auth calls
def read_protected(user : UserOutput = Depends(get_current_user)):
    return {"data": user}


def cleanup_files(*paths: Path): #have to decide if we want to keep the pdf in storage
    for path in paths:
        try:
            path.unlink(missing_ok=True)
            print(f"[CLEANUP] Deleted: {path.name}")
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")


# /process_pdf and download_file are temporary entpoints without db
@app.post("/process-pdf/")
async def process_pdf_api(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None,
    db : Session = Depends(get_db),
    user: UserOutput = Depends(get_current_user)
    ):

    #create a user specific directory
    user_dir = UPLOAD_DIR / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_id = uuid.uuid4().hex
    file_path = user_dir / f"{unique_id}{file_ext}"

    # Save uploaded file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process and get output file
    output_file, charts_json = process_pdf(file_path) #final processed FilePath
    print(f"[DEBUG] Output from process_pdf: {output_file}")

    if not output_file or not output_file.exists():
        raise HTTPException(status_code=500, detail="Processing failed")
        # Schedule cleanup in the background

        # return FileResponse(
        #     path=output_file,
        #     filename="processed_output.xlsx",
        #     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )

    path = f"uploads/{user.id}/{output_file.name}"

    service = UserService(session=db)
    file_data = UserFileCreate(
        filename = file.filename,
        download_path = path,
        json_charts = charts_json
    )
    user_file = service.add_user_file(user_id=user.id, file_data=file_data)

    return user_file
@app.get("/download/{file_name}")
async def download_file(file_name: str, background_tasks : BackgroundTasks):
    file_path = UPLOAD_DIR/ file_name
    if file_path.exists():
        return FileResponse(
             path=file_path,
             filename="processed_output.xlsx",
             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        raise HTTPException(status_code= 404, details = "File not found")