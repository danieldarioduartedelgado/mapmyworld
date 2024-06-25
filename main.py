from fastapi import FastAPI, Request, Query, Path
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from routers.location import router as location_router
from routers.category import router as category_router
from routers.review import router as review_router
from exceptiondef import GenericException
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")
app = FastAPI()


app.include_router(location_router)
app.include_router(category_router)
app.include_router(review_router)


# Manejador de excepciones para elevar mensajes de error de validacion en la app
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Custom exception", "errors": exc.errors()}
    )
# Manejador de excepciones para elevar mensajes de error genericos en la app
@app.exception_handler(GenericException)
async def generic_exception_handler(request: Request, exc: GenericException):
    return JSONResponse(
        status_code=418,
        content={"detail": "Custom Generic exception", "error": exc.message}
    )

# Manejador de excepciones para validacion de request, valida tipos de dato de 
# entrada en el API
@app.exception_handler(RequestValidationError)
async def req_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Custom Request Validation exception", "errors": exc.errors()}
    )

