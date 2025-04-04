from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from main import process_pdf

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

@app.post("/process-pdf/")
async def process_pdf_api(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    # Save uploaded file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process the PDF and get the output file
    output_file = process_pdf(file_path)

    if output_file and output_file.exists():
        return FileResponse(
            path=output_file,
            filename="processed_output.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        raise HTTPException(status_code=500, detail="Processing failed")
