from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


class CourseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DROPPED = "dropped"


@dataclass
class User:
    id: str = field(default_factory=lambda: f"u_{uuid.uuid4().hex[:8]}")
    name: str = ""
    email: str = ""
    phone: str = ""
    timezone: str = "Asia/Kolkata"
    learning_style: str = "visual"  # visual, auditory, reading, kinesthetic
    streak_days: int = 0
    last_active_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Course:
    id: str = field(default_factory=lambda: f"course_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    duration_hours: int = 10
    modules: int = 10
    category: str = "programming"
    difficulty: str = "beginner"  # beginner, intermediate, advanced


@dataclass
class Enrollment:
    id: str = field(default_factory=lambda: f"enroll_{uuid.uuid4().hex[:8]}")
    user_id: str = ""
    course_id: str = ""
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    progress: int = 0  # 0-100
    current_module: int = 1
    started_at: datetime = field(default_factory=datetime.now)
    last_activity_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Certificate:
    id: str = field(default_factory=lambda: f"cert_{uuid.uuid4().hex[:8]}")
    user_id: str = ""
    course_id: str = ""
    enrollment_id: str = ""
    issued_at: datetime = field(default_factory=datetime.now)


# In-memory storage for demo
class Database:
    def __init__(self):
        self.users: dict[str, User] = {}
        self.courses: dict[str, Course] = {}
        self.enrollments: dict[str, Enrollment] = {}
        self.certificates: dict[str, Certificate] = {}

    def clear(self):
        self.users.clear()
        self.courses.clear()
        self.enrollments.clear()
        self.certificates.clear()

    def get_user_enrollments(self, user_id: str) -> list[Enrollment]:
        return [e for e in self.enrollments.values() if e.user_id == user_id]

    def get_user_certificates(self, user_id: str) -> list[Certificate]:
        return [c for c in self.certificates.values() if c.user_id == user_id]


db = Database()
