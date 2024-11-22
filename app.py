from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Create an asynchronous engine for SQLite database
engine = create_async_engine("sqlite+aiosqlite:///baller.db", connect_args={"check_same_thread": False})
# Create an asynchronous session maker
SessionLocal = async_sessionmaker(engine)

# Define a base class for declarative class definitions
class Base(DeclarativeBase):
    pass

# Define a User model
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key column
    username: Mapped[str] = mapped_column(unique=True)  # Unique username column

# Dependency to get the database session
async def get_db():
    # Create all tables in the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db  # Provide the session to the caller
    finally:
        await db.close()  # Ensure the session is closed

# Pydantic model for User
class UserBase(BaseModel):
    username: str


# FASTAPI
app = FastAPI()

@app.post("/user")
async def index(user: UserBase, db: AsyncSession = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/user")
async def get_users(db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    return {"users": users}