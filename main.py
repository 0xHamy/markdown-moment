from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.database import Base, engine, get_db
from database.models import User, Course, Module, Section, Exercise
from routers import courses, auth
import bcrypt
import os, yaml, base64

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(courses.router)
app.include_router(auth.router)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

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
        # Upload minimal test course
        if not os.path.exists('MyCyber/course.yaml') or not os.path.exists('MyCyber/creator.yaml'):
            course = Course(yaml_id='mycyber', title='Test Course', points=100, creator_info=yaml.dump({"authors": [{"name": "Test Author"}], "editors": [], "contributors": [], "thanks": ""}))
            db.add(course)
            db.commit()
            module = Module(course_id=course.id, yaml_id='module1', title='Test Module', points=50, order=0)
            db.add(module)
            db.commit()
            section1 = Section(module_id=module.id, yaml_id='section1', title='Test Section 1', content=base64.b64encode('# Section 1'.encode()).decode(), points=10, order=0)
            section2 = Section(module_id=module.id, yaml_id='section2', title='Test Section 2', content=base64.b64encode('# Section 2'.encode()).decode(), points=10, order=1)
            exercise = Exercise(module_id=module.id, content=base64.b64encode('# Exercise'.encode()).decode(), points=20)
            db.add_all([section1, section2, exercise])
            db.commit()
        else:
            from routers.courses import upload_course
            upload_course('MyCyber/course.yaml', 'MyCyber/creator.yaml', 'MyCyber', db)
        print("Database initialized, test_user and admin created, course loaded")
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    os.makedirs("Uploads", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)

