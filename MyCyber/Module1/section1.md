# Section 1: Introduction

Welcome to MyCyber!

![Intro Image](../media/nuclear.png)


```python
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
```



