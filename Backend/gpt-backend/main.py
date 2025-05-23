from fastapi import FastAPI
from routers import auth_router, schedule_router
from database import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(schedule_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "API 서버가 정상 동작 중입니다."}
