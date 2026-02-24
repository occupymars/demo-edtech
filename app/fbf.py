"""Fourbyfour SDK integration for edtech vertical."""

from fourbyfour import edtech
from app.config import config

# Initialize the Fourbyfour client for edtech vertical
fbf = edtech(
    api_key=config.FOURBYFOUR_API_KEY,
    project_id=config.FOURBYFOUR_PROJECT_ID,
    base_url=config.FOURBYFOUR_BASE_URL,
)


async def track_course_enrolled(
    user_id: str,
    course_id: str,
    course_name: str,
    category: str,
):
    """Track when a user enrolls in a course."""
    return fbf.track("course.enrolled", {
        "user_id": user_id,
        "course_id": course_id,
        "course_name": course_name,
        "category": category,
    })


async def track_course_abandoned(
    user_id: str,
    course_id: str,
    course_name: str,
    progress: int,
    last_active_at: str,
):
    """Track when a user abandons a course."""
    return fbf.track("course.abandoned", {
        "user_id": user_id,
        "course_id": course_id,
        "course_name": course_name,
        "progress": progress,
        "last_active_at": last_active_at,
    })


async def track_streak_broken(
    user_id: str,
    streak_days: int,
    last_active_at: str,
):
    """Track when a learning streak is broken."""
    return fbf.track("streak.broken", {
        "user_id": user_id,
        "streak_days": streak_days,
        "last_active_at": last_active_at,
    })


async def track_certificate_earned(
    user_id: str,
    course_id: str,
    course_name: str,
    certificate_id: str,
):
    """Track when a user earns a certificate."""
    return fbf.track("certificate.earned", {
        "user_id": user_id,
        "course_id": course_id,
        "course_name": course_name,
        "certificate_id": certificate_id,
    })


async def track_level_completed(
    user_id: str,
    course_id: str,
    module_number: int,
    total_modules: int,
    progress: int,
):
    """Track when a user completes a module/level."""
    return fbf.track("level.completed", {
        "user_id": user_id,
        "course_id": course_id,
        "module_number": module_number,
        "total_modules": total_modules,
        "progress": progress,
    })


async def notify_user_context(
    user_id: str,
    timezone: str,
    preferred_channel: str = "email",
    learning_style: str = "visual",
    language: str = "en",
):
    """Send user context to help optimize delivery."""
    return fbf.notify({
        "user_id": user_id,
        "timezone": timezone,
        "preferred_channel": preferred_channel,
        "learning_style": learning_style,
        "language": language,
    })
