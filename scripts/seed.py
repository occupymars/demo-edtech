#!/usr/bin/env python3
"""Seed script to populate demo data for the edtech app."""

import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from app.models import db, User, Course, Enrollment, EnrollmentStatus

fake = Faker("en_IN")

# Sample courses
COURSES = [
    {"name": "Python for Beginners", "category": "programming", "difficulty": "beginner", "duration_hours": 20, "modules": 12},
    {"name": "Data Science Fundamentals", "category": "data-science", "difficulty": "intermediate", "duration_hours": 40, "modules": 20},
    {"name": "Machine Learning A-Z", "category": "ai-ml", "difficulty": "advanced", "duration_hours": 60, "modules": 30},
    {"name": "Web Development Bootcamp", "category": "web-dev", "difficulty": "beginner", "duration_hours": 50, "modules": 25},
    {"name": "JavaScript Mastery", "category": "programming", "difficulty": "intermediate", "duration_hours": 30, "modules": 15},
    {"name": "React & Next.js", "category": "web-dev", "difficulty": "intermediate", "duration_hours": 35, "modules": 18},
    {"name": "SQL for Data Analysis", "category": "data-science", "difficulty": "beginner", "duration_hours": 15, "modules": 10},
    {"name": "Deep Learning Specialization", "category": "ai-ml", "difficulty": "advanced", "duration_hours": 80, "modules": 40},
]

LEARNING_STYLES = ["visual", "auditory", "reading", "kinesthetic"]


def seed_courses() -> list[Course]:
    """Create courses."""
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
        print(f"Created course: {course.name} ({course.id})")

    return courses


def seed_users(count: int = 10) -> list[User]:
    """Create fake users."""
    users = []
    timezones = ["Asia/Kolkata", "Asia/Mumbai", "America/New_York", "Europe/London"]

    for i in range(count):
        streak = random.choice([0, 0, 0, 3, 7, 14, 21, 30])  # Some with streaks
        user = User(
            name=fake.name(),
            email=fake.email(),
            phone=f"+91{fake.msisdn()[3:13]}",
            timezone=timezones[i % len(timezones)],
            learning_style=LEARNING_STYLES[i % len(LEARNING_STYLES)],
            streak_days=streak,
            last_active_at=datetime.now() - timedelta(days=random.randint(0, 14)),
            created_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )
        users.append(user)
        db.users[user.id] = user
        print(f"Created user: {user.name} ({user.id}) - {streak} day streak")

    return users


def seed_enrollments(users: list[User], courses: list[Course]) -> list[Enrollment]:
    """Create enrollments for users."""
    enrollments = []
    statuses = [
        EnrollmentStatus.ACTIVE,
        EnrollmentStatus.ACTIVE,
        EnrollmentStatus.ACTIVE,
        EnrollmentStatus.PAUSED,
        EnrollmentStatus.DROPPED,
    ]

    for user in users:
        # Each user enrolls in 1-3 courses
        num_enrollments = random.randint(1, 3)
        user_courses = random.sample(courses, min(num_enrollments, len(courses)))

        for course in user_courses:
            status = random.choice(statuses)
            progress = random.randint(0, 100) if status != EnrollmentStatus.ACTIVE else random.randint(10, 80)
            current_module = max(1, int((progress / 100) * course.modules))

            enrollment = Enrollment(
                user_id=user.id,
                course_id=course.id,
                status=status,
                progress=progress,
                current_module=current_module,
                started_at=fake.date_time_between(start_date="-6M", end_date="now"),
                last_activity_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            )
            enrollments.append(enrollment)
            db.enrollments[enrollment.id] = enrollment
            print(f"Created enrollment: {user.name} → {course.name} ({progress}%)")

    return enrollments


def main():
    """Main seed function."""
    print("=" * 50)
    print("Seeding demo-edtech database...")
    print("=" * 50)

    # Clear existing data
    db.clear()

    # Seed data
    courses = seed_courses()
    users = seed_users(10)
    enrollments = seed_enrollments(users, courses)

    print("=" * 50)
    print(f"Seeded {len(courses)} courses, {len(users)} users, {len(enrollments)} enrollments")
    print("=" * 50)

    # Print summary
    print("\nSample learners:")
    for user in users[:3]:
        print(f"  - {user.name} ({user.email}) - {user.streak_days} day streak")

    print("\nRun the app with: uvicorn app.main:app --reload --port 8001")


if __name__ == "__main__":
    main()
