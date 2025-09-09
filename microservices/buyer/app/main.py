from fastapi import FastAPI
from database import lifespan
from routers import request_parts
from routers import action_quote

app = FastAPI(lifespan=lifespan)

# include auth routes

app.include_router(request_parts.router)
app.include_router(action_quote.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Buyer API "} 
    

