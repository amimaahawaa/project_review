# Project Review Management System

A Django-based web application for managing project reviews, student groups, and teacher-student interactions in an educational environment.

## Features

- **User Management**: Admin, Teacher, and Student roles with different permissions
- **Project Management**: Create topics, form groups, and manage project submissions
- **Review System**: Teachers can review and provide feedback on student submissions
- **Group Chat**: Real-time messaging within project groups
- **Dashboard**: Role-based dashboards with statistics and quick actions

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd projectReview
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install "Django==5.2.4" "django-widget-tweaks"
```

### 4. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## User Roles & Access

### Admin
- **Login**: `http://127.0.0.1:8000/admin-login/`
- **Dashboard**: `http://127.0.0.1:8000/dashboard/`
- **Permissions**: Manage teachers, students, and admins

### Teacher
- **Login**: `http://127.0.0.1:8000/login/`
- **Dashboard**: `http://127.0.0.1:8000/teacher-dashboard/`
- **Permissions**: 
  - Create project topics
  - Form student groups
  - Review project submissions
  - Access group chats

### Student
- **Signup**: `http://127.0.0.1:8000/signup/`
- **Login**: `http://127.0.0.1:8000/login/`
- **Dashboard**: `http://127.0.0.1:8000/student-dashboard/`
- **Permissions**:
  - Join project groups
  - Submit projects
  - Access group chats
  - View submission status

## Project Structure

```
projectReview/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── project_review/          # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── project_review_app/      # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # App URL patterns
│   ├── forms.py            # Django forms
│   └── migrations/         # Database migrations
└── templates/              # HTML templates
    ├── admin/              # Admin templates
    ├── teacher/            # Teacher templates
    ├── student/            # Student templates
    └── chat/               # Chat templates
```

## Key Models

- **CustomUser**: Extended user model with roles (admin, teacher, student)
- **Topic**: Project topics created by teachers
- **ProjectGroup**: Student groups assigned to topics
- **Submission**: Project submissions by students
- **ChatRoom/ChatMessage**: Group chat functionality

## Common Commands

### Database Operations
```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development
```bash
# Run development server
python manage.py runserver

# Run with custom port
python manage.py runserver 8080

# Run with custom host
python manage.py runserver 0.0.0.0:8000
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'widget_tweaks'**
   ```bash
   pip install django-widget-tweaks
   ```

2. **Database errors**
   ```bash
   python manage.py migrate
   ```

3. **Permission denied errors**
   - Ensure you're logged in with the correct role
   - Check if the user has the required permissions

4. **No projects showing in teacher dashboard**
   - Ensure groups are assigned to the logged-in teacher
   - Check if students have submitted projects
   - Verify the group's `teacher` field is set correctly

### Debug Mode
The application runs in DEBUG mode by default. For production:
1. Set `DEBUG = False` in `project_review/settings.py`
2. Configure `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL, MySQL)
4. Set up static file serving

## API Endpoints

### Authentication
- `POST /login/` - User login
- `POST /signup/` - Student registration
- `GET /logout/` - User logout

### Teacher Endpoints
- `GET /teacher-dashboard/` - Teacher dashboard
- `GET /teacher/submissions/` - View submissions
- `POST /teacher/submission/<id>/review/` - Review submission
- `GET /groups/` - List project groups
- `POST /teacher/create-topic/` - Create project topic

### Student Endpoints
- `GET /student-dashboard/` - Student dashboard
- `POST /project-submission/` - Submit project
- `GET /my-submissions/` - View own submissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
