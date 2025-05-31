from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from main import process_pdf
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="web", html=True), name="static")


def cleanup_files(*paths: Path):
    for path in paths:
        try:
            path.unlink(missing_ok=True)
            print(f"[CLEANUP] Deleted: {path.name}")
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")


@app.post("/process-pdf/")
async def process_pdf_api(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_id = uuid.uuid4().hex
    file_path = UPLOAD_DIR / f"{unique_id}{file_ext}"

    # Save uploaded file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process and get output file
    output_file, frontend_json = process_pdf(file_path) #final processed FilePath
    print(f"[DEBUG] Output from process_pdf: {output_file}")

    if output_file and output_file.exists():
        print(f"[DEBUG] File exists: {output_file}")
        # Schedule cleanup in the background

        # return FileResponse(
        #     path=output_file,
        #     filename="processed_output.xlsx",
        #     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )

        download_url = f"/download/{output_file.name}"

        return JSONResponse(content={
            "download_url" : download_url,
            "data" : frontend_json
        })
    else:
        #print(f"[ERROR] File missing or invalid: {output_file}")
        raise HTTPException(status_code=500, detail="Processing failed")
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