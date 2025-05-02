from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from functools import wraps
import os
import tempfile
import zipfile
import shutil
import yaml
import base64
import markdown
import bcrypt
from .models import Course, Module, Section, Exercise, User, Completion

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('app:auth_page')
        return view_func(request, *args, **kwargs)
    return wrapper

class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

@admin_required
def upload_page(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file.name.endswith('.zip'):
            messages.error(request, 'Please upload a .zip file')
            return render(request, 'upload.html')
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'course.zip')
            with open(zip_path, 'wb') as buffer:
                shutil.copyfileobj(file, buffer)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            course_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
            course_yaml = os.path.join(course_dir, 'course.yaml')
            creator_yaml = os.path.join(course_dir, 'creator.yaml')
            if not os.path.exists(course_yaml) or not os.path.exists(creator_yaml):
                messages.error(request, 'Missing course.yaml or creator.yaml')
                return render(request, 'upload.html')
            with open(course_yaml, 'r') as f:
                course_data = yaml.safe_load(f)
            with open(creator_yaml, 'r') as f:
                creator_data = yaml.dump(yaml.safe_load(f))
            course_yaml_id = course_data['course']['id']
            if Course.objects.filter(yaml_id=course_yaml_id).exists():
                messages.error(request, f"Course with ID {course_yaml_id} already exists")
                return render(request, 'upload.html')
            course = Course.objects.create(
                id=Course.objects.count() + 1,
                yaml_id=course_yaml_id,
                title=course_data['course']['title'],
                points=course_data['course']['points'],
                creator_info=creator_data
            )
            media_src = os.path.join(course_dir, 'media')
            media_dest = os.path.join('app', 'static', 'media', course_yaml_id)
            if os.path.exists(media_src):
                shutil.copytree(media_src, media_dest, dirs_exist_ok=True)
            for idx, mod in enumerate(course_data['course']['modules']):
                module = Module.objects.create(
                    id=Module.objects.count() + 1,
                    course=course,
                    yaml_id=mod['id'],
                    title=mod['title'],
                    points=mod['points'],
                    order=idx
                )
                for s_idx, sec in enumerate(mod['sections']):
                    with open(os.path.join(course_dir, sec['file']), 'r') as f:
                        content = f.read()
                    content = content.replace('../media/', f'/static/media/{course_yaml_id}/')
                    content_b64 = base64.b64encode(content.encode()).decode()
                    Section.objects.create(
                        id=Section.objects.count() + 1,
                        module=module,
                        yaml_id=sec['id'],
                        title=sec['title'],
                        content=content_b64,
                        points=sec['points'],
                        order=s_idx
                    )
                if 'exercise' in mod:
                    with open(os.path.join(course_dir, mod['exercise']['file']), 'r') as f:
                        content = f.read()
                    content = content.replace('../media/', f'/static/media/{course_yaml_id}/')
                    content_b64 = base64.b64encode(content.encode()).decode()
                    Exercise.objects.create(
                        id=Exercise.objects.count() + 1,
                        module=module,
                        content=content_b64,
                        points=mod['exercise']['points']
                    )
            messages.success(request, 'Course uploaded successfully')
            return redirect('app:upload_page')
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'upload.html', {'messages': messages_list})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already registered')
            return render(request, 'auth.html')
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        User.objects.create(
            id=User.objects.count() + 1,
            username=username,
            hashed_password=hashed_password,
            points=0
        )
        messages.success(request, 'User registered successfully')
        return redirect('app:login')
    return render(request, 'auth.html')

@login_required
def complete(request, item_type, item_id):
    if item_type not in ['section', 'exercise', 'course']:
        return JsonResponse({'detail': 'Invalid item type'}, status=400)
    Completion.objects.create(
        id=Completion.objects.count() + 1,
        user=request.user,
        item_type=item_type,
        item_id=item_id
    )
    if item_type == 'section':
        section = Section.objects.filter(id=item_id).first()
        if not section:
            return JsonResponse({'detail': 'Section not found'}, status=404)
        request.user.points += section.points
    elif item_type == 'exercise':
        exercise = Exercise.objects.filter(id=item_id).first()
        if not exercise:
            return JsonResponse({'detail': 'Exercise not found'}, status=404)
        request.user.points += section.points
    elif item_type == 'course':
        course = Course.objects.filter(id=item_id).first()
        if not course:
            return JsonResponse({'detail': 'Course not found'}, status=404)
        request.user.points += course.points
    if item_type in ['section', 'exercise']:
        module = None
        if item_type == 'section':
            section = Section.objects.filter(id=item_id).first()
            module = section.module
        else:
            exercise = Exercise.objects.filter(id=item_id).first()
            module = exercise.module
        module_sections = module.sections.all()
        module_exercise = module.exercise.first()
        completed_items = set(
            (c.item_type, c.item_id) for c in Completion.objects.filter(user=request.user)
        )
        module_completed = all(
            ('section', section.id) in completed_items for section in module_sections
        ) and (
            not module_exercise or ('exercise', module_exercise.id) in completed_items
        )
        if module_completed and ('module', module.id) not in completed_items:
            Completion.objects.create(
                id=Completion.objects.count() + 1,
                user=request.user,
                item_type='module',
                item_id=module.id
            )
            request.user.points += module.points
    request.user.save()
    return JsonResponse({'message': 'Completion recorded'})

@login_required
def courses(request):
    courses = Course.objects.all()
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'courses.html', {
        'courses': courses,
        'messages': messages_list
    })

@login_required
def dashboard(request):
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'dashboard.html', {
        'username': request.user.username,
        'messages': messages_list
    })

@login_required
def course(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return render(request, '404.html', status=404)
    modules = Module.objects.filter(course_id=course_id).order_by('order')
    creator_info = yaml.safe_load(course.creator_info)
    completed_items = set(
        (c.item_type, c.item_id) for c in Completion.objects.filter(user=request.user)
    )
    all_items_completed = True
    for module in modules:
        for section in module.sections.all():
            if ('section', section.id) not in completed_items:
                all_items_completed = False
                break
        if module.exercise.first() and ('exercise', module.exercise.first.id) not in completed_items:
            all_items_completed = False
        if not all_items_completed:
            break
    course_completed = ('course', course.id) in completed_items
    can_complete_course = all_items_completed and not course_completed
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'course.html', {
        'course': course,
        'modules': modules,
        'creator_info': creator_info,
        'can_complete_course': can_complete_course,
        'completed_items': completed_items,
        'messages': messages_list
    })

@login_required
def section(request, section_id):
    section = Section.objects.filter(id=section_id).first()
    if not section:
        return render(request, '404.html', status=404)
    course = section.module.course
    modules = Module.objects.filter(course_id=course.id).order_by('order')
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
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'section.html', {
        'section': section,
        'course': course,
        'modules': modules,
        'content': html_content,
        'has_sidebar': True,
        'messages': messages_list
    })

@login_required
def exercise(request, exercise_id):
    exercise = Exercise.objects.filter(id=exercise_id).first()
    if not exercise:
        return render(request, '404.html', status=404)
    course = exercise.module.course
    modules = Module.objects.filter(course_id=course.id).order_by('order')
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
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'exercise.html', {
        'exercise': exercise,
        'course': course,
        'modules': modules,
        'content': html_content,
        'has_sidebar': True,
        'messages': messages_list
    })

@login_required
def profile(request):
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'profile.html', {
        'username': request.user.username,
        'total_score': request.user.points,
        'messages': messages_list
    })

def auth_page(request):
    if request.user.is_authenticated:
        return redirect('app:dashboard')
    return render(request, 'auth.html')