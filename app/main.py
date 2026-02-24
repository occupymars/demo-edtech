"""Demo EdTech App - Showcasing Fourbyfour Integration."""

from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import config
from app.models import db, User, Course, Enrollment, Certificate, EnrollmentStatus
from app import fbf

app = FastAPI(
    title="LearnHub Demo",
    description="A demo edtech app showcasing Fourbyfour integration",
    version="0.1.0",
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ============================================================================
# Pages
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard showing all users and courses."""
    users = list(db.users.values())
    courses = list(db.courses.values())
    enrollments = list(db.enrollments.values())
    certificates = list(db.certificates.values())

    # Stats
    total_users = len(users)
    active_learners = len([e for e in enrollments if e.status == EnrollmentStatus.ACTIVE])
    abandoned = len([e for e in enrollments if e.progress > 0 and e.progress < 100 and
                     (datetime.now() - e.last_activity_at).days > 7])
    total_certificates = len(certificates)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "users": users,
        "courses": courses,
        "enrollments": enrollments,
        "certificates": certificates,
        "stats": {
            "total_users": total_users,
            "active_learners": active_learners,
            "abandoned": abandoned,
            "total_certificates": total_certificates,
        },
    })


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail(request: Request, user_id: str):
    """User detail page."""
    user = db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_enrollments = db.get_user_enrollments(user_id)
    user_certificates = db.get_user_certificates(user_id)

    # Enrich enrollments with course info
    enriched_enrollments = []
    for enrollment in user_enrollments:
        course = db.courses.get(enrollment.course_id)
        enriched_enrollments.append({
            "enrollment": enrollment,
            "course": course,
        })

    return templates.TemplateResponse("user_detail.html", {
        "request": request,
        "user": user,
        "enrollments": enriched_enrollments,
        "certificates": user_certificates,
        "courses": list(db.courses.values()),
    })


# ============================================================================
# Actions - Trigger Fourbyfour Events
# ============================================================================

@app.post("/actions/course-enrolled")
async def trigger_course_enrolled(
    user_id: str = Form(...),
    course_id: str = Form(...),
):
    """Trigger course.enrolled event."""
    user = db.users.get(user_id)
    course = db.courses.get(course_id)

    if not user or not course:
        raise HTTPException(status_code=404, detail="User or course not found")

    # Create enrollment
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        status=EnrollmentStatus.ACTIVE,
        progress=0,
    )
    db.enrollments[enrollment.id] = enrollment

    # Track event with Fourbyfour
    await fbf.track_course_enrolled(
        user_id=user_id,
        course_id=course_id,
        course_name=course.name,
        category=course.category,
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        learning_style=user.learning_style,
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/course-abandoned")
async def trigger_course_abandoned(
    user_id: str = Form(...),
    enrollment_id: str = Form(...),
):
    """Trigger course.abandoned event."""
    user = db.users.get(user_id)
    enrollment = db.enrollments.get(enrollment_id)

    if not user or not enrollment:
        raise HTTPException(status_code=404, detail="User or enrollment not found")

    course = db.courses.get(enrollment.course_id)

    # Update enrollment status
    enrollment.status = EnrollmentStatus.DROPPED
    enrollment.last_activity_at = datetime.now() - timedelta(days=14)

    # Track event with Fourbyfour
    await fbf.track_course_abandoned(
        user_id=user_id,
        course_id=enrollment.course_id,
        course_name=course.name if course else "Unknown",
        progress=enrollment.progress,
        last_active_at=enrollment.last_activity_at.isoformat(),
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        learning_style=user.learning_style,
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/streak-broken")
async def trigger_streak_broken(
    user_id: str = Form(...),
):
    """Trigger streak.broken event."""
    user = db.users.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    streak_before = user.streak_days
    user.streak_days = 0
    user.last_active_at = datetime.now() - timedelta(days=2)

    # Track event with Fourbyfour
    await fbf.track_streak_broken(
        user_id=user_id,
        streak_days=streak_before,
        last_active_at=user.last_active_at.isoformat(),
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        learning_style=user.learning_style,
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/certificate-earned")
async def trigger_certificate_earned(
    user_id: str = Form(...),
    enrollment_id: str = Form(...),
):
    """Trigger certificate.earned event."""
    user = db.users.get(user_id)
    enrollment = db.enrollments.get(enrollment_id)

    if not user or not enrollment:
        raise HTTPException(status_code=404, detail="User or enrollment not found")

    course = db.courses.get(enrollment.course_id)

    # Complete the enrollment
    enrollment.status = EnrollmentStatus.COMPLETED
    enrollment.progress = 100
    enrollment.completed_at = datetime.now()

    # Create certificate
    certificate = Certificate(
        user_id=user_id,
        course_id=enrollment.course_id,
        enrollment_id=enrollment_id,
    )
    db.certificates[certificate.id] = certificate

    # Track event with Fourbyfour
    await fbf.track_certificate_earned(
        user_id=user_id,
        course_id=enrollment.course_id,
        course_name=course.name if course else "Unknown",
        certificate_id=certificate.id,
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        learning_style=user.learning_style,
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/level-completed")
async def trigger_level_completed(
    user_id: str = Form(...),
    enrollment_id: str = Form(...),
):
    """Trigger level.completed event."""
    user = db.users.get(user_id)
    enrollment = db.enrollments.get(enrollment_id)

    if not user or not enrollment:
        raise HTTPException(status_code=404, detail="User or enrollment not found")

    course = db.courses.get(enrollment.course_id)

    # Progress to next module
    if course:
        enrollment.current_module = min(enrollment.current_module + 1, course.modules)
        enrollment.progress = int((enrollment.current_module / course.modules) * 100)
        enrollment.last_activity_at = datetime.now()

    # Track event with Fourbyfour
    await fbf.track_level_completed(
        user_id=user_id,
        course_id=enrollment.course_id,
        module_number=enrollment.current_module,
        total_modules=course.modules if course else 10,
        progress=enrollment.progress,
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


# ============================================================================
# API Endpoints (for load testing)
# ============================================================================

@app.post("/api/events/course-abandoned")
async def api_course_abandoned(
    user_id: str,
    course_id: str,
    course_name: str,
    progress: int = 35,
    last_active_at: str = None,
):
    """API endpoint for triggering course.abandoned event."""
    if not last_active_at:
        last_active_at = (datetime.now() - timedelta(days=14)).isoformat()

    result = await fbf.track_course_abandoned(
        user_id=user_id,
        course_id=course_id,
        course_name=course_name,
        progress=progress,
        last_active_at=last_active_at,
    )

    return {"status": "tracked", "event": "course.abandoned", "result": result}


@app.post("/api/events/streak-broken")
async def api_streak_broken(
    user_id: str,
    streak_days: int = 7,
    last_active_at: str = None,
):
    """API endpoint for triggering streak.broken event."""
    if not last_active_at:
        last_active_at = (datetime.now() - timedelta(days=2)).isoformat()

    result = await fbf.track_streak_broken(
        user_id=user_id,
        streak_days=streak_days,
        last_active_at=last_active_at,
    )

    return {"status": "tracked", "event": "streak.broken", "result": result}


@app.post("/api/events/certificate-earned")
async def api_certificate_earned(
    user_id: str,
    course_id: str,
    course_name: str,
    certificate_id: str = None,
):
    """API endpoint for triggering certificate.earned event."""
    if not certificate_id:
        certificate_id = f"cert_{user_id[-8:]}"

    result = await fbf.track_certificate_earned(
        user_id=user_id,
        course_id=course_id,
        course_name=course_name,
        certificate_id=certificate_id,
    )

    return {"status": "tracked", "event": "certificate.earned", "result": result}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "demo-edtech",
        "fourbyfour_configured": bool(config.FOURBYFOUR_API_KEY),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.APP_PORT)
