# SkillHub

SkillHub is a cyberpunk-inspired, neon-themed university project hub built with Flask and Jinja. It features a modern, responsive interface for managing courses, tasks, and student submissions, with a vibrant color palette:

- Neon Pink: #ff00cc
- Cyan: #00fff7
- Deep Blue: #1a0033

## Features

- **Modern UI/UX**: Responsive design with Bootstrap 5 and Font Awesome icons
- **Template Inheritance**: Clean, maintainable code using Jinja2 templating
- **Database Integration**: SQLAlchemy ORM with comprehensive data models
- **User Authentication**: Registration, login, and role-based access control
- **Course Management**: Create, view, and manage educational courses
- **Task System**: Assign and submit tasks with grading capabilities
- **Chat System**: Course-based messaging with media support
- **Responsive Design**: Optimized for all devices and screen sizes
- **Security**: Basic security measures with password hashing

## Technology Stack

### Backend
- **Python 3.x**: Core programming language
- **Flask 3.0.0**: Web framework
- **SQLAlchemy 2.0.23**: Object-Relational Mapping
- **Flask-Login**: User session management
- **Jinja2**: Template engine
- **Werkzeug**: WSGI utility library

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Styling with custom CSS
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library
- **JavaScript**: Interactive components

### Database
- **SQLite**: Development database (can be changed to PostgreSQL/MySQL for production)
- **Flask-Migrate**: Database migrations

## Project Structure

```
SkillHub/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # SQLAlchemy database models
├── database.py            # Database initialization and sample data
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore file
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template with navigation
│   ├── home.html         # Home page
│   ├── about.html        # About page
│   ├── contact.html      # Contact page
│   ├── courses.html      # Courses listing
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── profile.html      # User profile page
└── static/               # Static files (CSS, JS, images)
```

## Database Schema

The application includes a comprehensive database schema with the following main entities:

### Core Tables (Required - T)
1. **User**: User authentication and role management
2. **UserProfile**: Additional user information
3. **Course**: Course information and management
4. **Task**: Educational tasks and assignments
5. **UserAnswer**: Student submissions and evaluations
6. **CourseChat**: Course communication settings
7. **Message**: Chat messages with media support
8. **User_Courses**: Student-course enrollment
9. **Course_Tasks**: Task-course assignments

### Feature Tables (Optional - F)
1. **Tag**: Course categorization and filtering
2. **Course_Tags**: Course-tag relationships
3. **Course_Broadcast**: Live streaming functionality
4. **Broadcast_Participants**: Stream participation management

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd SkillHub
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
# Initialize database tables
python database.py init

# Create sample data (optional)
python database.py sample

# Or do both at once
python database.py full
```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Database Management

### Available Commands
```bash
python database.py init    # Create database tables
python database.py sample  # Add sample data
python database.py reset   # Reset database (delete all data)
python database.py full    # Initialize and add sample data
```

### Sample Data
The application comes with pre-configured sample data:
- **Admin User**: username: `admin`, password: `admin123`
- **Teacher User**: username: `teacher`, password: `teacher123`
- **Student User**: username: `student`, password: `student123`
- Sample courses, tasks, and tags

## Usage

### Available Routes
- `/` - Home page with course overview and statistics
- `/courses` - Browse all available courses with filtering
- `/course/<id>` - View specific course details
- `/about` - Detailed information about the project
- `/contact` - Contact form and information
- `/login` - User authentication
- `/register` - User registration
- `/profile` - User profile and statistics
- `/logout` - User logout

### API Endpoints
- `/api/courses` - Get all courses (JSON)
- `/api/course/<id>/tasks` - Get tasks for specific course (JSON)

### Features
1. **User Management**: Registration, login, role-based access
2. **Course Browsing**: View courses with filtering and pagination
3. **Authentication**: Secure login/logout with session management
4. **Responsive Design**: Works on desktop, tablet, and mobile
5. **Database Integration**: Full CRUD operations with SQLAlchemy

## Development

### Adding New Models
1. Define the model in `models.py`
2. Create database migration: `flask db migrate -m "Add new model"`
3. Apply migration: `flask db upgrade`

### Adding New Pages
1. Create a new route in `app.py`
2. Create a corresponding template in `templates/`
3. Extend the base template using `{% extends "base.html" %}`

### Database Relationships
The application uses SQLAlchemy relationships:
- **One-to-One**: User ↔ UserProfile
- **One-to-Many**: User → Courses (teaching), Course → Tasks
- **Many-to-Many**: Users ↔ Courses (enrollment), Courses ↔ Tags

## Security Considerations

- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection (can be added with Flask-WTF)
- Input validation and sanitization
- SQL injection protection via SQLAlchemy

## Deployment

### Production Setup
1. Set environment variables:
   ```bash
   export SECRET_KEY="your-secure-secret-key"
   export DATABASE_URL="postgresql://user:pass@localhost/dbname"
   export FLASK_ENV="production"
   ```

2. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

### Environment Variables
- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Application environment (development/production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

&copy; 2025 SkillHub. All rights reserved.

## Support

For support and questions, please contact:
- Email: info@skillhub.edu
- Phone: +1 (234) 567-890

## Future Enhancements

- File upload functionality
- Real-time chat with WebSockets
- Video streaming integration
- Advanced search and filtering
- Email notifications
- Mobile app API
- Advanced analytics and reporting

## Default Login Credentials

The database can be seeded with the following default users for testing purposes by running `python database.py sample`.

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Full access to the system.

### Teacher Accounts
- **Username:** `teacher1`
- **Password:** `teacher123`
- **Role:** Can create and manage their own courses.

- **Username:** `teacher2`
- **Password:** `teacher123`
- **Role:** Can create and manage their own courses.

### Student Accounts
- **Username:** `student1`
- **Password:** `student123`
- **Role:** Can enroll in courses and submit tasks.

- **Username:** `student2`
- **Password:** `student123`
- **Role:** Can enroll in courses and submit tasks.

- **Username:** `student3`
- **Password:** `student123`
- **Role:** Can enroll in courses and submit tasks. 
