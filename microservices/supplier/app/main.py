from fastapi import FastAPI
from database import lifespan
from routers import browse_parts


app = FastAPI(lifespan=lifespan)

# include auth routes

app.include_router(browse_parts.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Supplier API "} 
    

