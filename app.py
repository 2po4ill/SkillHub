from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, UserProfile, Course, Task, Tag, CourseChat, UserAnswer, Message, CourseBroadcast, course_tasks
from config import config
from datetime import datetime
import os
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FloatField, BooleanField, SelectMultipleField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Optional

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add Jinja filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if text:
            return text.replace('\n', '<br>')
        return text
    
    return app

app = create_app()

@app.route('/')
def home():
    """Home page with course overview"""
    courses = Course.query.filter_by(is_active=True, is_approved=True).limit(6).all()
    total_courses = Course.query.filter_by(is_active=True, is_approved=True).count()
    total_students = User.query.filter(User.is_teacher == False).count()
    total_teachers = User.query.filter_by(is_teacher=True).count()
    
    return render_template('home.html', 
                         title='Home',
                         courses=courses,
                         total_courses=total_courses,
                         total_students=total_students,
                         total_teachers=total_teachers)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html', title='About')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html', title='Contact')

@app.route('/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submission"""
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if name and email and message:
        # Here you would typically save to database or send email
        flash('Thank you for your message! We will get back to you soon.', 'success')
    else:
        flash('Please fill in all fields.', 'error')
    
    return redirect(url_for('contact'))

@app.route('/courses')
def courses():
    """Display all available courses"""
    page = request.args.get('page', 1, type=int)
    courses = Course.query.filter_by(is_active=True, is_approved=True).paginate(
        page=page, per_page=9, error_out=False)
    tags = Tag.query.all()
    
    return render_template('courses.html', 
                         title='Courses',
                         courses=courses,
                         tags=tags)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """Display course details"""
    course = Course.query.get_or_404(course_id)
    tasks = course.tasks
    students_count = len(course.students)
    
    return render_template('course_detail.html',
                         title=course.title,
                         course=course,
                         tasks=tasks,
                         students_count=students_count)

# FORMS
class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    max_students_allowed = IntegerField('Max Students', validators=[DataRequired()])
    price = FloatField('Price', validators=[Optional()])
    is_active = BooleanField('Active')
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    teacher_id = SelectField('Teacher', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Course')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    value = IntegerField('Value', validators=[Optional()])
    is_exam = BooleanField('Is Exam')
    start_date = DateTimeField('Start Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    deadline = DateTimeField('Deadline', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    solution = TextAreaField('Solution', validators=[Optional()])
    submit = SubmitField('Save Task')

# Course Management Routes
@app.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    form = CourseForm()
    # The teacher_id field is only relevant for admins creating courses for others
    if current_user.is_admin:
        form.teacher_id.choices = [(u.user_id, u.username) for u in User.query.filter_by(is_teacher=True).all()]
    else:
        del form.teacher_id
        
    form.tags.choices = [(t.tag_id, t.title) for t in Tag.query.order_by('title').all()]

    if form.validate_on_submit():
        # If user is admin, they can assign a teacher. Otherwise, they are the teacher.
        teacher_id = form.teacher_id.data if current_user.is_admin else current_user.user_id
        
        course = Course(
            title=form.title.data,
            description=form.description.data,
            teacher_id=teacher_id,
            max_students_allowed=form.max_students_allowed.data,
            price=form.price.data,
            is_active=form.is_active.data,
            is_approved=False  # All new courses require approval
        )

        selected_tags = Tag.query.filter(Tag.tag_id.in_(form.tags.data)).all()
        course.tags = selected_tags
        
        db.session.add(course)

        # Promote user to teacher if they aren't one already
        if not current_user.is_teacher:
            current_user.is_teacher = True
            db.session.add(current_user)
            flash('Congratulations! You are now a teacher. Your course is pending approval from an admin.', 'info')
        else:
            flash('Your course has been submitted and is pending approval.', 'success')

        db.session.commit()
        
        return redirect(url_for('course_detail', course_id=course.course_id))

    return render_template('course_form.html', title='Create Course', form=form, legend='New Course')

@app.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_admin and current_user.user_id != course.teacher_id:
        flash('You do not have permission to edit this course.', 'danger')
        return redirect(url_for('course_detail', course_id=course.course_id))

    form = CourseForm(obj=course)
    form.tags.choices = [(t.tag_id, t.title) for t in Tag.query.order_by('title').all()]
    if current_user.is_admin:
        form.teacher_id.choices = [(u.user_id, u.username) for u in User.query.filter_by(is_teacher=True).all()]
    else:
        del form.teacher_id
        
    if form.validate_on_submit():
        form.populate_obj(course)
        if current_user.is_admin:
            course.teacher_id = form.teacher_id.data
            
        selected_tags = Tag.query.filter(Tag.tag_id.in_(form.tags.data)).all()
        course.tags = selected_tags
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course.course_id))
    elif request.method == 'GET':
        form.tags.data = [tag.tag_id for tag in course.tags]
        if current_user.is_admin:
            form.teacher_id.data = course.teacher_id

    return render_template('course_form.html', title='Edit Course', form=form, legend=f'Edit {course.title}', course=course)

@app.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll a student in a course"""
    course = Course.query.get_or_404(course_id)
    
    if current_user.user_id == course.teacher_id:
        flash('Teachers cannot enroll in their own courses.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    if current_user in course.students:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    if len(course.students) >= course.max_students_allowed:
        flash('This course is full.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    try:
        course.students.append(current_user)
        db.session.commit()
        flash('Successfully enrolled in the course!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error enrolling in course. Please try again.', 'error')
    
    return redirect(url_for('course_detail', course_id=course_id))

# Task Management Routes
@app.route('/course/<int:course_id>/tasks')
@login_required
def manage_tasks(course_id):
    """Manage tasks for a course"""
    course = Course.query.get_or_404(course_id)
    
    if not current_user.is_admin and current_user.user_id != course.teacher_id:
        flash('You do not have permission to manage tasks for this course.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    tasks = course.tasks
    pending_tasks = [task for task in tasks if task.answers and not all(answer.is_reviewed for answer in task.answers)]
    graded_tasks = [task for task in tasks if task.answers and all(answer.is_reviewed for answer in task.answers)]
    
    return render_template('manage_tasks.html',
                         title='Manage Tasks',
                         course=course,
                         tasks=tasks,
                         pending_tasks=pending_tasks,
                         graded_tasks=graded_tasks)

@app.route('/course/<int:course_id>/task/add', methods=['GET', 'POST'])
@login_required
def add_task(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.user_id != course.teacher_id and not current_user.is_admin:
        flash('You do not have permission to add tasks to this course.', 'danger')
        return redirect(url_for('course_detail', course_id=course.course_id))

    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            value=form.value.data,
            solution=form.solution.data
        )
        db.session.add(task)
        db.session.flush()

        course_task_assoc = course_tasks.insert().values(
            course_id=course.course_id,
            task_id=task.task_id,
            is_exam=form.is_exam.data,
            start_date=form.start_date.data,
            deadline=form.deadline.data
        )
        db.session.execute(course_task_assoc)
        db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course.course_id))

    return render_template('task_form.html', title='New Task', form=form, course=course, legend='New Task')

@app.route('/course/<int:course_id>/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(course_id, task_id):
    course = Course.query.get_or_404(course_id)
    task = Task.query.get_or_404(task_id)

    if not current_user.is_admin and current_user.user_id != course.teacher_id:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('task_detail', course_id=course.course_id, task_id=task.task_id))

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        form.populate_obj(task)
        task.due_date = form.deadline.data
        db.session.commit()
        flash('Task has been updated!', 'success')
        return redirect(url_for('task_detail', course_id=course.course_id, task_id=task.task_id))

    return render_template('task_form.html', title='Edit Task', form=form, legend=f'Edit Task: {task.title}', course=course, task=task)

@app.route('/course/<int:course_id>/task/<int:task_id>')
@login_required
def task_detail(course_id, task_id):
    """View task details and submissions"""
    course = Course.query.get_or_404(course_id)
    task = Task.query.get_or_404(task_id)
    
    if task not in course.tasks:
        flash('Task not found in this course.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Check if user is enrolled or is the teacher
    if current_user not in course.students and current_user.user_id != course.teacher_id and not current_user.is_admin:
        flash('You must be enrolled in this course to view tasks.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Get user's submission if they're a student
    user_submission = None
    if current_user in course.students:
        user_submission = UserAnswer.query.filter_by(
            task_id=task_id, 
            user_id=current_user.user_id
        ).first()
    
    # Get all submissions if user is teacher/admin
    all_submissions = None
    if current_user.user_id == course.teacher_id or current_user.is_admin:
        all_submissions = UserAnswer.query.filter_by(task_id=task_id).all()
    
    return render_template('task_detail.html',
                         title=task.title,
                         course=course,
                         task=task,
                         user_submission=user_submission,
                         all_submissions=all_submissions)

@app.route('/course/<int:course_id>/task/<int:task_id>/submit', methods=['POST'])
@login_required
def submit_task(course_id, task_id):
    """Submit an answer to a task"""
    course = Course.query.get_or_404(course_id)
    task = Task.query.get_or_404(task_id)
    
    if task not in course.tasks:
        flash('Task not found in this course.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    if current_user not in course.students:
        flash('You must be enrolled in this course to submit answers.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    user_answer = request.form.get('user_answer')
    
    if not user_answer:
        flash('Please provide an answer.', 'error')
        return redirect(url_for('task_detail', course_id=course_id, task_id=task_id))
    
    try:
        # Check if user already submitted
        existing_submission = UserAnswer.query.filter_by(
            task_id=task_id, 
            user_id=current_user.user_id
        ).first()
        
        if existing_submission:
            # Update existing submission
            existing_submission.user_answer = user_answer
            existing_submission.update_date = datetime.utcnow()
            flash('Your answer has been updated!', 'success')
        else:
            # Create new submission
            submission = UserAnswer(
                task_id=task_id,
                user_id=current_user.user_id,
                user_answer=user_answer,
                creation_date=datetime.utcnow(),
                is_reviewed=False
            )
            db.session.add(submission)
            flash('Your answer has been submitted!', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash('Error submitting answer. Please try again.', 'error')
    
    return redirect(url_for('task_detail', course_id=course_id, task_id=task_id))

@app.route('/course/<int:course_id>/task/<int:task_id>/grade', methods=['GET', 'POST'])
@login_required
def grade_task(course_id, task_id):
    course = Course.query.get_or_404(course_id)
    task = Task.query.get_or_404(task_id)

    if not current_user.is_admin and current_user.user_id != course.teacher_id:
        flash('You do not have permission to grade tasks for this course.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    if request.method == 'POST':
        answer_id = request.form.get('answer_id')
        evaluation = request.form.get('evaluation')

        if not answer_id or not evaluation:
            flash('Missing submission information.', 'danger')
            return redirect(url_for('grade_task', course_id=course_id, task_id=task_id))

        submission = UserAnswer.query.get_or_404(answer_id)
        
        # Security check to ensure the submission belongs to this task
        if submission.task_id != task.task_id:
            abort(403)

        submission.evaluation = int(evaluation)
        submission.is_reviewed = True
        db.session.commit()

        flash(f'Submission for {submission.user.username} has been graded.', 'success')
        return redirect(url_for('grade_task', course_id=course_id, task_id=task_id))

    submissions = UserAnswer.query.filter_by(task_id=task_id).all()
    return render_template('grade_task.html', title=f"Grade Task: {task.title}",
                         course=course, task=task, submissions=submissions)

@app.route('/course/<int:course_id>/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(course_id, task_id):
    """Delete a task"""
    course = Course.query.get_or_404(course_id)
    task = Task.query.get_or_404(task_id)
    
    if not current_user.is_admin and current_user.user_id != course.teacher_id:
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    if task not in course.tasks:
        return jsonify({'success': False, 'message': 'Task not found in course'})
    
    try:
        # Remove task from course
        course.tasks.remove(task)
        
        # Delete the task
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_banned:
            flash('This account has been banned.', 'danger')
            return redirect(url_for('login'))
        
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', title='Login')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', title='Register')

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', title='Profile')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    pending_courses = Course.query.filter_by(is_approved=False).order_by(Course.creation_date.desc()).all()
    
    return render_template('admin_dashboard.html', 
                         title='Admin Dashboard',
                         pending_courses=pending_courses)

@app.route('/admin/approve_course/<int:course_id>', methods=['POST'])
@login_required
def approve_course(course_id):
    if not current_user.is_admin:
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    course.is_approved = True
    db.session.commit()
    
    flash(f"Course '{course.title}' has been approved.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_and_ban/<int:course_id>', methods=['POST'])
@login_required
def delete_and_ban(course_id):
    if not current_user.is_admin:
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    teacher = course.teacher
    
    # Ban the user
    teacher.is_banned = True
    
    # Delete the course
    db.session.delete(course)
    db.session.commit()
    
    flash(f"Course '{course.title}' has been deleted and user '{teacher.username}' has been banned.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/api/courses')
def api_courses():
    """API endpoint for courses"""
    courses = Course.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': course.course_id,
        'title': course.title,
        'description': course.description,
        'price': course.price,
        'max_students': course.max_students_allowed,
        'teacher': course.teacher.username if course.teacher else None,
        'tags': [tag.title for tag in course.tags]
    } for course in courses])

@app.route('/api/course/<int:course_id>/tasks')
def api_course_tasks(course_id):
    """API endpoint for course tasks"""
    course = Course.query.get_or_404(course_id)
    tasks = course.tasks
    return jsonify([{
        'id': task.task_id,
        'title': task.title,
        'description': task.description,
        'value': task.value
    } for task in tasks])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 