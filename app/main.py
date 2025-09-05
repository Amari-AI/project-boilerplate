from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging
from app.api.routes import router
import uvicorn

setup_logging()
app = FastAPI(title="Document Processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Document Processing API"} 

if __name__ == "__main__":
    # Use import string to allow --reload mode when launched as a module
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
