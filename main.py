from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()



@app.get("/")
async def head_root():
    return JSONResponse(status_code=200)
async def read_root():
    return {"message": "Welcome to the Auto Parts Marketplace API"} 
    