from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

import api


app = FastAPI()
app.include_router(api.router, prefix="/api")
app.mount("/", StaticFiles(directory="/static", html=True), name="frontend")
