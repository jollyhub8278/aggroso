from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import claims, reviews
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Claim Policy Review Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims.router)
app.include_router(reviews.router)


@app.get("/")
def root():
    return {"message": "Expense Claim Policy Review Assistant API"}
