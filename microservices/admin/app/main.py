from fastapi import FastAPI
from database import lifespan
from routers import users_manage
from routers import logs
from routers import vehicle_manage
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include auth routes
app.include_router(users_manage.router)
app.include_router(logs.router)
app.include_router(vehicle_manage.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Admin API "} 
    
