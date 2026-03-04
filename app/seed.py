"""Seed database with demo data."""

import random
from datetime import datetime, timedelta
from app.models import db, User, Course, Enrollment, EnrollmentStatus

# Sample courses
COURSES = [
    {"name": "Python for Beginners", "category": "programming", "difficulty": "beginner", "duration_hours": 20, "modules": 12},
    {"name": "Data Science Fundamentals", "category": "data-science", "difficulty": "intermediate", "duration_hours": 40, "modules": 20},
    {"name": "Machine Learning A-Z", "category": "ai-ml", "difficulty": "advanced", "duration_hours": 60, "modules": 30},
    {"name": "Web Development Bootcamp", "category": "web-dev", "difficulty": "beginner", "duration_hours": 50, "modules": 25},
    {"name": "JavaScript Mastery", "category": "programming", "difficulty": "intermediate", "duration_hours": 30, "modules": 15},
    {"name": "React & Next.js", "category": "web-dev", "difficulty": "intermediate", "duration_hours": 35, "modules": 18},
]

# Sample users
USERS = [
    {"name": "Priya Sharma", "email": "priya@example.com", "streak": 14},
    {"name": "Rahul Patel", "email": "rahul@example.com", "streak": 7},
    {"name": "Anita Gupta", "email": "anita@example.com", "streak": 0},
    {"name": "Vikram Singh", "email": "vikram@example.com", "streak": 30},
    {"name": "Neha Kapoor", "email": "neha@example.com", "streak": 3},
]

LEARNING_STYLES = ["visual", "auditory", "reading", "kinesthetic"]


def seed_database():
    """Seed the database with demo data."""
    print("Seeding database...")
    db.clear()

    # Create courses
    courses = []
    for course_data in COURSES:
        course = Course(
            name=course_data["name"],
            description=f"Learn {course_data['name']} from scratch",
            category=course_data["category"],
            difficulty=course_data["difficulty"],
            duration_hours=course_data["duration_hours"],
            modules=course_data["modules"],
        )
        courses.append(course)
        db.courses[course.id] = course

    # Create users
    users = []
    for i, user_data in enumerate(USERS):
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            phone=f"+91987654321{i}",
            timezone="Asia/Kolkata",
            learning_style=LEARNING_STYLES[i % len(LEARNING_STYLES)],
            streak_days=user_data["streak"],
            last_active_at=datetime.now() - timedelta(days=random.randint(0, 7)),
        )
        users.append(user)
        db.users[user.id] = user

    # Create enrollments
    for user in users:
        num_enrollments = random.randint(1, 3)
        user_courses = random.sample(courses, min(num_enrollments, len(courses)))

        for course in user_courses:
            progress = random.randint(10, 90)
            current_module = max(1, int((progress / 100) * course.modules))

            enrollment = Enrollment(
                user_id=user.id,
                course_id=course.id,
                status=EnrollmentStatus.ACTIVE,
                progress=progress,
                current_module=current_module,
                started_at=datetime.now() - timedelta(days=random.randint(7, 60)),
                last_activity_at=datetime.now() - timedelta(days=random.randint(0, 14)),
            )
            db.enrollments[enrollment.id] = enrollment

    print(f"Seeded {len(courses)} courses, {len(users)} users, {len(db.enrollments)} enrollments")
