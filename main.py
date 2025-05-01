from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database.database import Base, engine, get_db
from database.models import User
from routers import courses, auth, templates
import bcrypt
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(courses.router)
app.include_router(auth.router)
app.include_router(templates.router)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

@app.get("/")
async def root():
    return RedirectResponse(url="/courses/")

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
    os.makedirs("Uploads", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)