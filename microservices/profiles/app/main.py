from fastapi import FastAPI
from database import lifespan
from routers import profiles


app = FastAPI(lifespan=lifespan)

# include auth routes

app.include_router(profiles.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Profile API "} 
    
