from fastapi import FastAPI
from database import lifespan
from routers import order_quote

app = FastAPI(lifespan=lifespan)

# include auth routes


app.include_router(order_quote.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts Order API "} 
    

