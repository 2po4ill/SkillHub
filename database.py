from flask import Flask
from flask_migrate import Migrate
from models import db, User, UserProfile, Course, Task, Tag, CourseChat
from config import config
import os

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app

def init_db():
    """Initialize the database with tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def create_sample_data():
    """Create sample data for testing"""
    app = create_app()
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            email='admin@unirepo.edu',
            is_admin=True,
            is_moderator=True,
            is_teacher=True
        )
        admin.set_password('admin123')
        
        # Create teacher user
        teacher = User(
            username='teacher',
            email='teacher@unirepo.edu',
            is_teacher=True
        )
        teacher.set_password('teacher123')
        
        # Create student user
        student = User(
            username='student',
            email='student@unirepo.edu'
        )
        student.set_password('student123')
        
        # Add users to database
        db.session.add(admin)
        db.session.add(teacher)
        db.session.add(student)
        db.session.commit()
        
        # Create user profiles
        admin_profile = UserProfile(
            user_id=admin.user_id,
            fullname='Administrator',
            city='University City',
            country='University Country',
            phone_number='+1234567890'
        )
        
        teacher_profile = UserProfile(
            user_id=teacher.user_id,
            fullname='Dr. John Smith',
            city='Academic City',
            country='Academic Country',
            phone_number='+1234567891'
        )
        
        student_profile = UserProfile(
            user_id=student.user_id,
            fullname='Alice Johnson',
            city='Student City',
            country='Student Country',
            phone_number='+1234567892'
        )
        
        db.session.add(admin_profile)
        db.session.add(teacher_profile)
        db.session.add(student_profile)
        db.session.commit()
        
        # Create tags
        tags = [
            Tag(color='FF6B6B', title='Programming'),
            Tag(color='4ECDC4', title='Mathematics'),
            Tag(color='45B7D1', title='Science'),
            Tag(color='96CEB4', title='Literature'),
            Tag(color='FFEAA7', title='History'),
            Tag(color='DDA0DD', title='Art')
        ]
        
        for tag in tags:
            db.session.add(tag)
        db.session.commit()
        
        # Create courses
        courses = [
            Course(
                teacher_id=teacher.user_id,
                title='Introduction to Python Programming',
                description='Learn the fundamentals of Python programming language',
                max_students_allowed=50,
                price=99.99,
                is_active=True,
                is_approved=True
            ),
            Course(
                teacher_id=teacher.user_id,
                title='Advanced Web Development',
                description='Master modern web development techniques',
                max_students_allowed=30,
                price=149.99,
                is_active=True,
                is_approved=True
            ),
            Course(
                teacher_id=admin.user_id,
                title='Database Design Principles',
                description='Learn database design and SQL',
                max_students_allowed=40,
                price=79.99,
                is_active=True,
                is_approved=True
            )
        ]
        
        for course in courses:
            db.session.add(course)
        db.session.commit()
        
        # Add tags to courses
        python_course = courses[0]
        python_course.tags.append(tags[0])  # Programming
        python_course.tags.append(tags[2])  # Science
        
        web_course = courses[1]
        web_course.tags.append(tags[0])  # Programming
        web_course.tags.append(tags[2])  # Science
        
        db_course = courses[2]
        db_course.tags.append(tags[0])  # Programming
        db_course.tags.append(tags[2])  # Science
        
        db.session.commit()
        
        # Create course chats
        for course in courses:
            chat = CourseChat(
                course_id=course.course_id,
                is_photo_allowed=True,
                is_video_allowed=True
            )
            db.session.add(chat)
        db.session.commit()
        
        # Create tasks
        tasks = [
            Task(
                title='Hello World Program',
                description='Create your first Python program that prints "Hello, World!"',
                solution='print("Hello, World!")',
                value=10
            ),
            Task(
                title='Variables and Data Types',
                description='Demonstrate understanding of Python variables and data types',
                solution='name = "John"\nage = 25\nheight = 1.75\nis_student = True',
                value=15
            ),
            Task(
                title='Web Page Structure',
                description='Create a basic HTML page with proper structure',
                solution='<!DOCTYPE html>\n<html>\n<head>\n<title>My Page</title>\n</head>\n<body>\n<h1>Hello</h1>\n</body>\n</html>',
                value=20
            )
        ]
        
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        
        # Assign tasks to courses
        python_course.tasks.append(tasks[0])
        python_course.tasks.append(tasks[1])
        web_course.tasks.append(tasks[2])
        
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"Created {len(courses)} courses, {len(tasks)} tasks, and {len(tags)} tags")

def reset_db():
    """Reset the database (delete all data and recreate tables)"""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            init_db()
        elif command == 'sample':
            create_sample_data()
        elif command == 'reset':
            reset_db()
        elif command == 'full':
            init_db()
            create_sample_data()
        else:
            print("Available commands: init, sample, reset, full")
    else:
        print("Usage: python database.py [init|sample|reset|full]")
        print("  init  - Initialize database tables")
        print("  sample - Create sample data")
        print("  reset - Reset database (delete all data)")
        print("  full  - Initialize and create sample data") 