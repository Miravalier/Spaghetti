from bson.errors import InvalidId
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import admin_endpoints
import api_endpoints


app = FastAPI()

@app.exception_handler(InvalidId)
async def bson_invalid_id_exception(request: Request, exc: InvalidId):
    return JSONResponse(
        status_code=400,
        content={"detail": "invalid object id"}
    )

app.include_router(admin_endpoints.router, prefix="/admin")
app.include_router(api_endpoints.router, prefix="/api")

app.mount("/", StaticFiles(directory="/static", html=True), name="frontend")
