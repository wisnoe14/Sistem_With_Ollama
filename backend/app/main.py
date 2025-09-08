from fastapi import FastAPI
from app.api.v1 import api_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FastAPI ChatGPT Integration")

# Middleware CORSM
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1/endpoints")

@app.get("/")
def root():
    return {"message": "FastAPI ChatGPT API is running"}
