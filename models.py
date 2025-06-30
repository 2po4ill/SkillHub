from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association Tables
user_courses = db.Table('user_courses',
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('join_date', db.DateTime, nullable=False, default=datetime.utcnow),
    db.Column('graduation_date', db.DateTime, nullable=True)
)

course_tasks = db.Table('course_tasks',
    db.Column('task_id', db.Integer, db.ForeignKey('task.task_id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'), primary_key=True),
    db.Column('is_exam', db.Boolean, nullable=False, default=False),
    db.Column('start_date', db.DateTime, nullable=True),
    db.Column('deadline', db.DateTime, nullable=True)
)

course_tags = db.Table('course_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'), primary_key=True)
)

broadcast_participants = db.Table('broadcast_participants',
    db.Column('broadcast_id', db.Integer, db.ForeignKey('course_broadcast.broadcast_id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('is_allowed_to_speak', db.Boolean, nullable=False, default=False)
)

class User(db.Model, UserMixin):
    """User model - stores user authentication and role data"""
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_moderator = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    courses_teaching = db.relationship('Course', backref='teacher', foreign_keys='Course.teacher_id')
    courses_enrolled = db.relationship('Course', secondary=user_courses, backref='students')
    answers = db.relationship('UserAnswer', backref='user', cascade='all, delete-orphan')
    messages_sent = db.relationship('Message', backref='sender', foreign_keys='Message.user_id')
    messages_received = db.relationship('Message', backref='target', foreign_keys='Message.target_id')
    broadcast_participations = db.relationship('CourseBroadcast', secondary=broadcast_participants, backref='participants')
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    """User profile model - stores additional user information"""
    __tablename__ = 'user_profile'
    
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    fullname = db.Column(db.String(150), nullable=True)
    image_path = db.Column(db.String(254), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    
    def __repr__(self):
        return f'<UserProfile {self.fullname}>'

class Course(db.Model):
    """Course model - stores course information"""
    __tablename__ = 'course'
    
    course_id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    max_students_allowed = db.Column(db.Integer, default=50)
    price = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', secondary=course_tasks, backref='courses')
    chat = db.relationship('CourseChat', backref='course', uselist=False, cascade='all, delete-orphan')
    broadcasts = db.relationship('CourseBroadcast', backref='course', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=course_tags, backref=db.backref('courses', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Task(db.Model):
    """Task model - stores task information"""
    __tablename__ = 'task'
    
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    solution = db.Column(db.Text, nullable=True)
    solution_img = db.Column(db.String(254), nullable=True)
    value = db.Column(db.Integer, nullable=True)
    
    # Relationships
    answers = db.relationship('UserAnswer', backref='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.title}>'

class UserAnswer(db.Model):
    """User answer model - stores user submissions"""
    __tablename__ = 'user_answer'
    
    answer_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    user_answer_adornment = db.Column(db.String(254), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    is_reviewed = db.Column(db.Boolean, nullable=False, default=False)
    evaluation = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<UserAnswer {self.answer_id}>'

class CourseChat(db.Model):
    """Course chat model - stores chat settings"""
    __tablename__ = 'course_chat'
    
    chat_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    is_photo_allowed = db.Column(db.Boolean, nullable=False, default=True)
    is_video_allowed = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    messages = db.relationship('Message', backref='chat', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CourseChat {self.chat_id}>'

class Message(db.Model):
    """Message model - stores chat messages"""
    __tablename__ = 'message'
    
    message_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('course_chat.chat_id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    reply_to = db.Column(db.Integer, nullable=True)
    photo_path = db.Column(db.String(254), nullable=True)
    video_path = db.Column(db.String(254), nullable=True)
    text = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.message_id}>'

class Tag(db.Model):
    """Tag model - stores course tags"""
    __tablename__ = 'tag'
    
    tag_id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(6), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.title}>'

class CourseBroadcast(db.Model):
    """Course broadcast model - stores live streaming information"""
    __tablename__ = 'course_broadcast'
    
    broadcast_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    is_recorded = db.Column(db.Boolean, nullable=False, default=False)
    record_path = db.Column(db.String(254), nullable=True)
    max_participants = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<CourseBroadcast {self.broadcast_id}>' 