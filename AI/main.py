from fastapi import FastAPI
from routers import auth_router, schedule_router, ai_router
from database import init_db
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import restaurant_router
from routers import mealdetail_router
from routers import desinationdetail_router

from routers import popular_router

from routers.budget_router import router as budget_router
from routers.quick_budget_router import router as quick_budget_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup 시 실행할 코드
    init_db()
    yield
    # shutdown 시 실행할 코드 (필요하면 여기에 추가)

app = FastAPI(lifespan=lifespan)
        
app.include_router(popular_router.router)
app.include_router(auth_router.router)
app.include_router(schedule_router.router)
app.include_router(ai_router.router)
app.include_router(restaurant_router.router)
app.include_router(budget_router)
app.include_router(quick_budget_router)
app.include_router(mealdetail_router.router)
app.include_router(desinationdetail_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API 서버가 정상 동작 중입니다."}
