from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import admin
import api


app = FastAPI()

app.include_router(admin.router, prefix="/admin")
app.include_router(api.router, prefix="/api")

app.mount("/", StaticFiles(directory="/static", html=True), name="frontend")
