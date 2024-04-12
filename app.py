from fastapi import FastAPI
from routing.auth import router as auth_router
from routing.banner import router as banner_router
from database.base import init_models


app = FastAPI()


app.include_router(auth_router)
app.include_router(banner_router)


@app.on_event("startup")
async def start():
    pass
    init_models()


if __name__ == "__main__":
    import uvicorn

    # uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=8) #  For stress test
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
