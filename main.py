from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import uvicorn

app = FastAPI()

# This route will respond to both GET and HEAD requests
@app.get("/", response_class=JSONResponse)
@app.head("/")
async def root():
    return {"message": "Welcome to the Auto Parts Marketplace API"}


# Run with Render's assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # default 8000 for local testing
    uvicorn.run(app, host="0.0.0.0", port=port)