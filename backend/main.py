from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import admin_endpoints
import api_endpoints


app = FastAPI()

app.include_router(admin_endpoints.router, prefix="/admin")
app.include_router(api_endpoints.router, prefix="/api")

app.mount("/", StaticFiles(directory="/static", html=True), name="frontend")
