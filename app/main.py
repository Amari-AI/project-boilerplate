from fastapi import FastAPI
from app.api.routes import router
import uvicorn

app = FastAPI(title="Document Processing API")

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Document Processing API"}


if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
