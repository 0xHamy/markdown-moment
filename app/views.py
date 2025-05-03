from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, logout
from functools import wraps
import os
import tempfile
import zipfile
import shutil
import yaml
import base64
import markdown
import bcrypt, json
from .models import Course, Module, Section, Exercise, User, Completion
from django.views.decorators.http import require_POST


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('app:auth_page')
        if not request.user.is_admin:
            return redirect('app:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def non_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return redirect('app:admin_dashboard')
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
            # Save and extract ZIP
            zip_path = os.path.join(temp_dir, 'course.zip')
            with open(zip_path, 'wb') as buffer:
                shutil.copyfileobj(file, buffer)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Files are at the root of temp_dir
            course_dir = temp_dir

            # Parse course_intro.yaml
            intro_yaml_path = os.path.join(course_dir, 'course_intro.yaml')
            if not os.path.exists(intro_yaml_path):
                messages.error(request, 'Missing course_intro.yaml')
                return render(request, 'upload.html')
            with open(intro_yaml_path, 'r') as f:
                intro_data = yaml.safe_load(f)

            # Parse course_structure.yaml
            structure_yaml_path = os.path.join(course_dir, 'course_structure.yaml')
            if not os.path.exists(structure_yaml_path):
                messages.error(request, 'Missing course_structure.yaml')
                return render(request, 'upload.html')
            with open(structure_yaml_path, 'r') as f:
                structure_data = yaml.safe_load(f)

            # Load and encode course_info.md
            info_md_path = os.path.join(course_dir, 'course_info.md')
            if not os.path.exists(info_md_path):
                messages.error(request, 'Missing course_info.md')
                return render(request, 'upload.html')
            with open(info_md_path, 'r') as f:
                overview_content = f.read()
            overview_b64 = base64.b64encode(overview_content.encode()).decode()

            # Check for duplicate course
            course_yaml_id = structure_data['course']['id']
            if Course.objects.filter(yaml_id=course_yaml_id).exists():
                messages.error(request, f"Course with ID {course_yaml_id} already exists")
                return render(request, 'upload.html')

            # Handle badge filename
            badge_key = 'badge' if 'badge' in intro_data else 'bagde'
            badge_filename = os.path.basename(intro_data.get(badge_key, ''))
            badge_path = f"/static/uploads/{course_yaml_id}/media/{badge_filename}" if badge_filename else None

            # Create Course
            course = Course.objects.create(
                yaml_id=course_yaml_id,
                title=intro_data['title'],
                points=structure_data['course']['points'],
                badge=badge_path,
                short_description=intro_data['short_description'],
                version=intro_data['version'],
                duration=intro_data['duration'],
                difficulty=intro_data['difficulty'],
                language=intro_data['language'],
                course_type=intro_data['type'],
                level=intro_data['level'],
                topics=intro_data.get('topics', []),
                overview=overview_b64
            )

            # Move media files
            media_src = os.path.join(course_dir, 'media')
            media_dest = os.path.join('app', 'static', 'uploads', course_yaml_id, 'media')
            if os.path.exists(media_src):
                shutil.copytree(media_src, media_dest, dirs_exist_ok=True)

            # Process modules, sections, and exercises
            for idx, mod in enumerate(structure_data['course']['modules']):
                module = Module.objects.create(
                    course=course,
                    yaml_id=mod['id'],
                    title=mod['title'],
                    description=mod.get('description', ''),
                    points=mod['points'],
                    order=idx
                )
                for s_idx, sec in enumerate(mod['sections']):
                    section_file = os.path.join(course_dir, sec['file'])
                    if not os.path.exists(section_file):
                        messages.error(request, f"Section file {sec['file']} not found")
                        return render(request, 'upload.html')
                    with open(section_file, 'r') as f:
                        content = f.read()
                    content = content.replace('../media/', f'/static/uploads/{course_yaml_id}/media/')
                    content_b64 = base64.b64encode(content.encode()).decode()
                    Section.objects.create(
                        module=module,
                        yaml_id=sec['id'],
                        title=sec['title'],
                        content=content_b64,
                        points=sec['points'],
                        order=s_idx
                    )
                if 'exercise' in mod:
                    exercise_file = os.path.join(course_dir, mod['exercise']['file'])
                    if not os.path.exists(exercise_file):
                        messages.error(request, f"Exercise file {mod['exercise']['file']} not found")
                        return render(request, 'upload.html')
                    with open(exercise_file, 'r') as f:
                        content = f.read()
                    content = content.replace('../media/', f'/static/uploads/{course_yaml_id}/media/')
                    content_b64 = base64.b64encode(content.encode()).decode()
                    Exercise.objects.create(
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
@non_admin_required
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
        request.user.points += exercise.points
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
@non_admin_required
def courses(request):
    courses = Course.objects.all()
    messages_list = [msg.message for msg in messages.get_messages(request)]
    courses_data = [
        {
            'id': course.id,
            'title': course.title,
            'short_description': course.short_description,
            'points': course.points,
            'language': course.language,
            'course_type': course.course_type,
            'difficulty': course.difficulty,
            'level': course.level,
            'duration': course.duration,
            'version': course.version,
            'badge': course.badge,
            'topics': json.loads(course.topics) if isinstance(course.topics, str) else course.topics if isinstance(course.topics, list) else []
        } for course in courses
    ]
    return render(request, 'courses.html', {
        'courses': courses_data,
        'messages': messages_list
    })


@login_required
@non_admin_required
def course_info(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        overview_bytes = base64.b64decode(course.overview)
        overview_md = overview_bytes.decode('utf-8')
        overview_html = markdown.markdown(overview_md, extensions=['extra', 'fenced_code'])
    except Exception as e:
        overview_html = '<p>Error rendering course overview.</p>'
    return render(request, 'course_info.html', {
        'course': course,
        'overview_html': overview_html
    })


@login_required
@non_admin_required
def dashboard(request):
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'dashboard.html', {
        'username': request.user.username,
        'messages': messages_list
    })

@login_required
@non_admin_required
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
@non_admin_required
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
@non_admin_required
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
@non_admin_required
def profile(request):
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'profile.html', {
        'username': request.user.username,
        'total_score': request.user.points,
        'messages': messages_list
    })

def auth_page(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('app:admin_dashboard')
        return redirect('app:dashboard')
    return render(request, 'auth.html')

@admin_required
def admin_dashboard(request):
    messages_list = [msg.message for msg in messages.get_messages(request)]
    return render(request, 'admin_dashboard.html', {
        'username': request.user.username,
        'messages': messages_list
    })

@login_required
@non_admin_required
@require_POST
def delete_account(request):
    password = request.POST.get('password', '')
    confirmation = request.POST.get('confirmation', '').lower() == 'delete'

    if not confirmation:
        return JsonResponse({'detail': 'Confirmation text incorrect.'}, status=400)
        
    if not bcrypt.checkpw(password.encode(), request.user.hashed_password.encode()):
        return JsonResponse({'detail': 'Password incorrect.'}, status=400)

    user = request.user
    logout(request)
    user.delete()

    return JsonResponse({'redirect':  redirect('app:auth_page').url})

