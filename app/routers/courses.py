from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import Course, Module, Section, Exercise, User, Completion
from app.schemas import CourseResponse, CompletionResponse
from app.database.database import get_db
from app.routers.auth import get_current_user

course_router = APIRouter(prefix="/course", tags=["Course Endpoints"])

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

