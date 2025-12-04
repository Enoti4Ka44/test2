from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager
import bcrypt
from .database import init_db, AsyncSessionLocal
from .models import User
from sqlalchemy import select
from .routers import auth, articles, source

async def create_admin_user():
    ADMIN_EMAIL = "a@a.com"
    ADMIN_PASSWORD = "admin" 
    ADMIN_USERNAME = "admin"

    hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.email == ADMIN_EMAIL)
        result = await session.execute(stmt)
        exists = result.scalar_one_or_none()
        
        if not exists:
            admin_user = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=hashed_password,
                role="admin"  
            )
            session.add(admin_user)
            await session.commit()
            print(f"Администратор с email '{ADMIN_EMAIL}' создан!")
        else:
            print(f"Администратор с email '{ADMIN_EMAIL}' уже существует.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await create_admin_user()
    yield 


app = FastAPI(
    title="News Aggregator API",
    description="API для агрегатора новостей с поддержкой JWT и RBAC.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(source.router, prefix="/sources", tags=["Sources"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])


