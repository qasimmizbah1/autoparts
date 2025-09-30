from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# This route will respond to both GET and HEAD requests
@app.get("/", response_class=JSONResponse)
@app.head("/")
async def root():
    return {"message": "Welcome to the Auto Parts Marketplace API"}
