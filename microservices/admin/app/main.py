from fastapi import FastAPI
from database import lifespan
from routers import manageadmin
from routers import logs
from routers import managevehicle

app = FastAPI(lifespan=lifespan)

# include auth routes
app.include_router(manageadmin.router)
app.include_router(logs.router)
app.include_router(managevehicle.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Admin API "} 
    
