from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.util.init_db import create_tables
from app.routers.auth import authrouter
from app.util.protectRoute import get_current_user
from app.db.schema.user import UserOutput
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app : FastAPI):
    #db startup initialization
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for testing 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=authrouter, tags=["auth"], prefix="/auth")

@app.get("/health")
def health_check():
    return {"status" : "Running..."}

@app.get("/protected")
def read_protected(user : UserOutput = Depends(get_current_user)):
    return {"data": user}

# this main shoud be merged with app.py (main -> app)