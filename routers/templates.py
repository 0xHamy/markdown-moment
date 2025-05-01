from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import asc
import yaml
import base64
import markdown
from database.database import get_db
from database.models import Course, Module, Section, Exercise, User, Completion
from routers.auth import get_current_user
from fastapi.requests import Request
from typing import Optional


templates_router = APIRouter(prefix="/academy", tags=["Base Academy Endpoints"])
templates = Jinja2Templates(directory="templates")


def get_current_active_user(current_user: Optional[User] = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/academy/auth")
    return current_user

@templates_router.get("/courses/", response_class=HTMLResponse)
async def courses(request: Request, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    courses = db.query(Course).all()
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse(
        "courses.html",
        {"request": request, "courses": courses, "messages": messages, "current_user": current_user}
    )

@templates_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_active_user)):
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "username": current_user.username, "messages": messages, "current_user": current_user}
    )

@templates_router.get("/courses/course/{course_id}", response_class=HTMLResponse)
async def course(request: Request, course_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    modules = db.query(Module).filter(Module.course_id == course_id).order_by(asc(Module.order)).all()
    creator_info = yaml.safe_load(course.creator_info)

    completed_items = set()
    can_complete_course = False
    if current_user:
        completed_items = set(
            (c.item_type, c.item_id) for c in db.query(Completion).filter(Completion.user_id == current_user.id).all()
        )
        all_items_completed = True
        for module in modules:
            for section in module.sections:
                if ('section', section.id) not in completed_items:
                    all_items_completed = False
                    break
            if module.exercise and ('exercise', module.exercise.id) not in completed_items:
                all_items_completed = False
            if not all_items_completed:
                break
        course_completed = ('course', course.id) in completed_items
        can_complete_course = all_items_completed and not course_completed

    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse(
        "course.html",
        {
            "request": request,
            "course": course,
            "modules": modules,
            "creator_info": creator_info,
            "can_complete_course": can_complete_course,
            "completed_items": completed_items,
            "messages": messages,
            "current_user": current_user
        }
    )

@templates_router.get("/courses/section/{section_id}", response_class=HTMLResponse)
async def section(request: Request, section_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    course = section.module.course
    modules = db.query(Module).filter(Module.course_id == course.id).order_by(asc(Module.order)).all()
    content_md = base64.b64decode(section.content).decode()
    html_content = markdown.markdown(
        content_md,
        extensions=['fenced_code', 'codehilite'],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            }
        }
    )
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse(
        "section.html",
        {
            "request": request,
            "section": section,
            "course": course,
            "modules": modules,
            "content": html_content,
            "has_sidebar": True,
            "messages": messages,
            "current_user": current_user
        }
    )

@templates_router.get("/courses/exercise/{exercise_id}", response_class=HTMLResponse)
async def exercise(request: Request, exercise_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    course = exercise.module.course
    modules = db.query(Module).filter(Module.course_id == course.id).order_by(asc(Module.order)).all()
    content_md = base64.b64decode(exercise.content).decode()
    html_content = markdown.markdown(
        content_md,
        extensions=['fenced_code', 'codehilite'],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            }
        }
    )
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse(
        "exercise.html",
        {
            "request": request,
            "exercise": exercise,
            "course": course,
            "modules": modules,
            "content": html_content,
            "has_sidebar": True,
            "messages": messages,
            "current_user": current_user
        }
    )

@templates_router.get("/courses/upload", response_class=HTMLResponse)
async def upload_page(request: Request, current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can access this page")
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse("upload.html", {"request": request, "messages": messages, "current_user": current_user})

@templates_router.get("/courses/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: User = Depends(get_current_active_user)):
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "username": current_user.username, "total_score": current_user.points, "messages": messages, "current_user": current_user}
    )

@templates_router.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})