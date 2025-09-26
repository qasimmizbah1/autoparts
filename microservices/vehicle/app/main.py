from fastapi import FastAPI
from database import lifespan
from routers import vehicle
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

# include auth routes

app.include_router(vehicle.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Vehicle API "} 
    
