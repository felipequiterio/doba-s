from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from starlette.exceptions import HTTPException

from api import router
from utils.log import get_custom_logger

app = FastAPI(
    version="0.0.1",
    title="DOBA Server",
    description="Endpoints to use DOBA",
)

logger = get_custom_logger("MIDDLEWARE")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"HTTP Error: {repr(exc)}")
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Invalid data: {exc}")
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    print(f"Global error handler data: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )


app.include_router(router)
