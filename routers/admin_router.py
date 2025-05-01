from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import yaml
import shutil
import base64
import zipfile
import tempfile
import os
from database.models import Course, Module, Section, Exercise, User
from database.database import get_db
from routers.auth import get_current_user
from typing import Optional

admin_router = APIRouter(prefix="/admin", tags=["Admin Endpoints"])
templates = Jinja2Templates(directory="templates")

def upload_course(course_yaml_path, creator_yaml_path, course_dir, db: Session):
    with open(course_yaml_path, 'r') as f:
        course_data = yaml.safe_load(f)
    with open(creator_yaml_path, 'r') as f:
        creator_data = yaml.dump(yaml.safe_load(f))

    course_yaml_id = course_data['course']['id']
    if db.query(Course).filter(Course.yaml_id == course_yaml_id).first():
        raise HTTPException(status_code=400, detail=f"Course with ID {course_yaml_id} already exists")

    course = Course(
        yaml_id=course_yaml_id,
        title=course_data['course']['title'],
        points=course_data['course']['points'],
        creator_info=creator_data
    )
    db.add(course)
    db.commit()

    media_src = os.path.join(course_dir, 'media')
    media_dest = os.path.join('static', 'media', course_yaml_id)
    if os.path.exists(media_src):
        shutil.copytree(media_src, media_dest, dirs_exist_ok=True)

    for idx, mod in enumerate(course_data['course']['modules']):
        module = Module(
            course_id=course.id,
            yaml_id=mod['id'],
            title=mod['title'],
            points=mod['points'],
            order=idx
        )
        db.add(module)
        db.commit()

        for s_idx, sec in enumerate(mod['sections']):
            with open(os.path.join(course_dir, sec['file']), 'r') as f:
                content = f.read()
            content = content.replace('../media/', f'/static/media/{course_yaml_id}/')
            content_b64 = base64.b64encode(content.encode()).decode()
            section = Section(
                module_id=module.id,
                yaml_id=sec['id'],
                title=sec['title'],
                content=content_b64,
                points=sec['points'],
                order=s_idx
            )
            db.add(section)

        if 'exercise' in mod:
            with open(os.path.join(course_dir, mod['exercise']['file']), 'r') as f:
                content = f.read()
            content = content.replace('../media/', f'/static/media/{course_yaml_id}/')
            content_b64 = base64.b64encode(content.encode()).decode()
            exercise = Exercise(
                module_id=module.id,
                content=content_b64,
                points=mod['exercise']['points']
            )
            db.add(exercise)

    db.commit()

def get_current_admin_user(current_user: Optional[User] = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/academy/auth")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can access this page")
    return current_user

@admin_router.get("/courses/upload", response_class=HTMLResponse)
async def upload_page(request: Request, current_user: User = Depends(get_current_admin_user)):
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse("upload.html", {"request": request, "messages": messages, "current_user": current_user})

@admin_router.post("/courses/upload")
async def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    request: Request = None
):
    if not file.filename.endswith('.zip'):
        messages = request.session.get('messages', [])
        messages.append("Please upload a .zip file")
        request.session['messages'] = messages
        raise HTTPException(status_code=400, detail="Please upload a .zip file")

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'course.zip')
        with open(zip_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        course_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        course_yaml = os.path.join(course_dir, 'course.yaml')
        creator_yaml = os.path.join(course_dir, 'creator.yaml')

        if not os.path.exists(course_yaml) or not os.path.exists(creator_yaml):
            messages = request.session.get('messages', [])
            messages.append("Missing course.yaml or creator.yaml")
            request.session['messages'] = messages
            raise HTTPException(status_code=400, detail="Missing course.yaml or creator.yaml")

        upload_course(course_yaml, creator_yaml, course_dir, db)
        messages = request.session.get('messages', [])
        messages.append("Course uploaded successfully")
        request.session['messages'] = messages
        return {"message": "Course uploaded successfully"}

