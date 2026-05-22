import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import analytics, import_data, customers, potential, export_data, actions

# Create DB tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Hệ thống Quản lý Khách hàng Bưu điện TP Huế")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router)
app.include_router(import_data.router)
app.include_router(customers.router)
app.include_router(potential.router)
app.include_router(actions.router)
app.include_router(export_data.router)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Khởi động KHHH Management System...")
