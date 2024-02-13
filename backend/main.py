from bson.errors import InvalidId
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import admin_endpoints
import api_endpoints


templates = Jinja2Templates(directory="/static")
app = FastAPI()

@app.exception_handler(InvalidId)
async def bson_invalid_id_exception(request: Request, exc: InvalidId):
    return JSONResponse(
        status_code=400,
        content={"detail": "invalid object id"}
    )

@app.get("/")
async def root(request: Request):
    return RedirectResponse("/account")

@app.get("/account", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="account.html")

@app.get("/friends", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="friends.html")

@app.get("/settings", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="settings.html")

@app.get("/login", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

app.include_router(admin_endpoints.router, prefix="/admin")
app.include_router(api_endpoints.router, prefix="/api")

app.mount("/", StaticFiles(directory="/static", html=True), name="frontend")
