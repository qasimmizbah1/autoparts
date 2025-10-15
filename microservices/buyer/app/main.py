from fastapi import FastAPI
from database import lifespan
from routers import request_parts
from routers import action_quote
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

app.include_router(request_parts.router)
app.include_router(action_quote.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Buyer API "} 
    

