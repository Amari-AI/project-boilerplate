from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
import uvicorn
import os

app = FastAPI(title="Document Processing API")

app.include_router(router)

# Serve static files from React build
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")


@app.get("/")
async def root():
    # Serve React app if build exists, otherwise API message
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    return {
        "message": "Welcome to the Document Processing API - React UI not built yet"
    }


if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
