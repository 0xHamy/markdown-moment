from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from app.database.database import Base, engine, get_db
from app.database.models import User
from app.routers.auth import auth_router
from app.routers.courses import course_router
from app.routers.templates import templates_router
from app.routers.admin_router import admin_router
from app.routers.auth import get_current_user
import bcrypt
import os
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="your-secure-secret-key")

app.include_router(course_router)
app.include_router(auth_router)
app.include_router(templates_router)
app.include_router(admin_router)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_307_TEMPORARY_REDIRECT and "Location" in exc.headers:
        return RedirectResponse(url=exc.headers["Location"], status_code=307)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )

@app.get("/")
async def index(current_user: Optional[User] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/academy/dashboard")
    return RedirectResponse(url="/academy/auth")

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        if not db.query(User).filter(User.username == 'test_user').first():
            hashed_password = get_password_hash("password1")
            test_user = User(username="test_user", hashed_password=hashed_password, points=0, is_admin=False)
            db.add(test_user)
        if not db.query(User).filter(User.username == 'admin').first():
            hashed_password = get_password_hash("1234567890")
            admin_user = User(username="admin", hashed_password=hashed_password, points=0, is_admin=True)
            db.add(admin_user)
        db.commit()
        print("Database initialized, test_user and admin created")
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    os.makedirs("app/Uploads", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)

