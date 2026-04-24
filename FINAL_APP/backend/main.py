from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Document Analysis API")

# include all routes
app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Backend running"}