from fastapi import FastAPI
from database import lifespan
from routers import manageadmin
from routers import logs

app = FastAPI(lifespan=lifespan)

# include auth routes
app.include_router(manageadmin.router)
app.include_router(logs.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Admin API "} 
    
