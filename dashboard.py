from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from status import get_status

app = FastAPI()

@app.get("/status")
def status():
    return get_status()

app.mount("/", StaticFiles(directory="static", html=True), name="static")