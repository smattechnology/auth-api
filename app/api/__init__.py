from fastapi import FastAPI, APIRouter, Request, Response, Depends
import pkgutil
import importlib

from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal, get_db
from app.service.device import DeviceService

app = FastAPI(root_path="/api")

class DeviceDetectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Create a DB session manually
        db: Session = SessionLocal()
        try:
            service = DeviceService(db)
            device_info = service.parse_and_log(request)
            request.state.device = device_info
        finally:
            db.close()  # Always close the session

        response = await call_next(request)
        return response

app.add_middleware(DeviceDetectionMiddleware)


for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith("_"):
        continue  # skip private/internal modules

    # Import the module dynamically
    module = importlib.import_module(f"{__name__}.{module_name}")
    # Include router if it exists
    router = getattr(module, "router", None)
    if router and isinstance(router, APIRouter):
        app.include_router(router)