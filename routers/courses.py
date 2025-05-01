from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import yaml
import shutil
import base64
import zipfile
import tempfile
import os
from database.models import Course, Module, Section, Exercise, User, Completion
from schemas import CourseResponse, CompletionResponse
from database.database import get_db
from routers.auth import get_current_user
from fastapi.requests import Request


course_router = APIRouter(prefix="/course", tags=["Course Endpoints"])


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

@course_router.post("/complete/{item_type}/{item_id}")
async def complete(item_type: str, item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if item_type not in ['section', 'exercise', 'course']:
        raise HTTPException(status_code=400, detail="Invalid item type")

    completion = Completion(user_id=current_user.id, item_type=item_type, item_id=item_id)
    db.add(completion)

    if item_type == 'section':
        section = db.query(Section).filter(Section.id == item_id).first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        current_user.points += section.points
    elif item_type == 'exercise':
        exercise = db.query(Exercise).filter(Exercise.id == item_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        current_user.points += exercise.points
    elif item_type == 'course':
        course = db.query(Course).filter(Course.id == item_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        current_user.points += course.points

    if item_type in ['section', 'exercise']:
        module = None
        if item_type == 'section':
            section = db.query(Section).filter(Section.id == item_id).first()
            module = section.module
        else:
            exercise = db.query(Exercise).filter(Exercise.id == item_id).first()
            module = exercise.module

        module_sections = module.sections
        module_exercise = module.exercise
        completed_items = set(
            (c.item_type, c.item_id) for c in db.query(Completion).filter(Completion.user_id == current_user.id).all()
        )

        module_completed = all(
            ('section', section.id) in completed_items for section in module_sections
        ) and (
            not module_exercise or ('exercise', module_exercise.id) in completed_items
        )

        if module_completed and ('module', module.id) not in completed_items:
            completion = Completion(user_id=current_user.id, item_type='module', item_id=module.id)
            db.add(completion)
            current_user.points += module.points

    db.commit()
    return {"message": "Completion recorded"}

@course_router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can upload courses")
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

