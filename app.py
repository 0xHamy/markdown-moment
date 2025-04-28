import os
import yaml
import shutil
import base64
import zipfile
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import markdown

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # For flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Database Models
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yaml_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "mycyber"
    title = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    creator_info = db.Column(db.Text)  # Store creator.yaml as YAML string
    modules = db.relationship('Module', backref='course', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    yaml_id = db.Column(db.String(50), nullable=False)  # e.g., "module1"
    title = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    order = db.Column(db.Integer, default=0)
    sections = db.relationship('Section', backref='module', lazy=True)
    exercise = db.relationship('Exercise', backref='module', uselist=False)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    yaml_id = db.Column(db.String(50), nullable=False)  # e.g., "section1"
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Base64-encoded Markdown
    points = db.Column(db.Integer, default=0)
    order = db.Column(db.Integer, default=0)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Base64-encoded Markdown
    points = db.Column(db.Integer, default=0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)

class Completion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # 'section' or 'exercise'
    item_id = db.Column(db.Integer, nullable=False)

# Upload Course Function
def upload_course(course_yaml_path, creator_yaml_path, course_dir):
    with open(course_yaml_path, 'r') as f:
        course_data = yaml.safe_load(f)
    with open(creator_yaml_path, 'r') as f:
        creator_data = yaml.dump(yaml.safe_load(f))  # Store as YAML string

    course_yaml_id = course_data['course']['id']
    if Course.query.filter_by(yaml_id=course_yaml_id).first():
        raise ValueError(f"Course with ID {course_yaml_id} already exists")

    course = Course(
        yaml_id=course_yaml_id,
        title=course_data['course']['title'],
        points=course_data['course']['points'],
        creator_info=creator_data
    )
    db.session.add(course)
    db.session.commit()

    # Copy media to course-specific directory
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
        db.session.add(module)
        db.session.commit()

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
            db.session.add(section)

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
            db.session.add(exercise)

    db.session.commit()

# Process Zipped Course
def process_zip(file):
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'course.zip')
        file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Assume course is in a single top-level folder
        course_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        course_yaml = os.path.join(course_dir, 'course.yaml')
        creator_yaml = os.path.join(course_dir, 'creator.yaml')

        if not os.path.exists(course_yaml) or not os.path.exists(creator_yaml):
            raise ValueError("Missing course.yaml or creator.yaml")

        try:
            upload_course(course_yaml, creator_yaml, course_dir)
        except ValueError as e:
            raise e

# Routes
@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/course/<int:course_id>')
def course(course_id):
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    creator_info = yaml.safe_load(course.creator_info)
    return render_template('course.html', course=course, modules=modules, creator_info=creator_info)

@app.route('/section/<int:section_id>')
def section(section_id):
    section = Section.query.get_or_404(section_id)
    content_md = base64.b64decode(section.content).decode()
    html_content = markdown.markdown(content_md)
    return render_template('section.html', section=section, content=html_content)

@app.route('/exercise/<int:exercise_id>')
def exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    content_md = base64.b64decode(exercise.content).decode()
    html_content = markdown.markdown(content_md)
    return render_template('exercise.html', exercise=exercise, content=html_content)

@app.route('/complete/<item_type>/<int:item_id>', methods=['POST'])
def complete(item_type, item_id):
    user = User.query.first()  # Simplified: assume first user
    if not user:
        user = User(username="test_user")
        db.session.add(user)
        db.session.commit()
    if item_type in ['section', 'exercise']:
        completion = Completion(user_id=user.id, item_type=item_type, item_id=item_id)
        db.session.add(completion)
        db.session.commit()
    return redirect(url_for('course', course_id=1))  # Adjust as needed

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and file.filename.endswith('.zip'):
            try:
                process_zip(file)
                flash('Course uploaded successfully')
                return redirect(url_for('index'))
            except ValueError as e:
                flash(str(e))
                return redirect(request.url)
        else:
            flash('Please upload a .zip file')
            return redirect(request.url)
    return render_template('upload.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.drop_all()  # Reset for example
        db.create_all()
        # Upload initial course for testing
        upload_course('MyCyber/course.yaml', 'MyCyber/creator.yaml', 'MyCyber')
    app.run(debug=True)

