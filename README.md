# Demo EdTech - LearnHub

A demo edtech learning platform showcasing [Fourbyfour](https://fourbyfour.dev) integration.

## Overview

LearnHub is a simulated online learning platform that demonstrates how to integrate Fourbyfour for automated engagement workflows:

- **Course Re-engagement** - Trigger `course.abandoned` when learners drop off
- **Streak Recovery** - Trigger `streak.broken` to bring back lapsed learners
- **Celebration** - Trigger `certificate.earned` to celebrate completions and upsell
- **Progress Updates** - Trigger `level.completed` for milestone notifications

## Quick Start

### 1. Install dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .
```

### 2. Configure Fourbyfour

```bash
cp .env.example .env
```

Edit `.env` with your Fourbyfour credentials:

```env
FOURBYFOUR_API_KEY=fbf_live_xxx
FOURBYFOUR_PROJECT_ID=proj_xxx
FOURBYFOUR_BASE_URL=https://api.fourbyfour.dev
```

### 3. Seed demo data

```bash
python scripts/seed.py
```

### 4. Run the app

```bash
uvicorn app.main:app --reload --port 8001
```

Open http://localhost:8001 to view the dashboard.

## Triggering Events

### Via UI

1. Go to the dashboard at http://localhost:8001
2. Click on a learner to view their details
3. Click any of the event trigger buttons:
   - **Enroll in Course** - Sends `course.enrolled` event
   - **Break Streak** - Sends `streak.broken` event
   - **Abandon Course** - Sends `course.abandoned` event
   - **Earn Certificate** - Sends `certificate.earned` event

### Via API

```bash
# Course abandoned
curl -X POST "http://localhost:8001/api/events/course-abandoned?user_id=u_123&course_id=course_456&course_name=Python%20Basics&progress=35"

# Streak broken
curl -X POST "http://localhost:8001/api/events/streak-broken?user_id=u_123&streak_days=7"

# Certificate earned
curl -X POST "http://localhost:8001/api/events/certificate-earned?user_id=u_123&course_id=course_456&course_name=Python%20Mastery"
```

## Load Testing

Run the load test script to benchmark event throughput:

```bash
# Default: 1000 events, 50 concurrent
python scripts/load_test.py

# Custom configuration
python scripts/load_test.py --events 5000 --concurrency 100

# Different event type
python scripts/load_test.py --event-type streak.broken
```

## Project Structure

```
demo-edtech/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app with routes
│   ├── config.py        # Configuration from env
│   ├── models.py        # Data models (User, Course, Enrollment)
│   └── fbf.py           # Fourbyfour SDK wrapper
├── templates/
│   ├── base.html        # Base template
│   ├── dashboard.html   # Main dashboard
│   └── user_detail.html # User detail + event triggers
├── scripts/
│   ├── seed.py          # Seed fake data
│   └── load_test.py     # Load testing script
├── static/              # Static assets
├── .env.example         # Environment template
├── pyproject.toml       # Dependencies
└── README.md
```

## Fourbyfour Integration

This app uses the [Fourbyfour Python SDK](https://pypi.org/project/fourbyfour/):

```python
from fourbyfour import edtech

fbf = edtech(
    api_key=os.environ["FOURBYFOUR_API_KEY"],
    project_id=os.environ["FOURBYFOUR_PROJECT_ID"],
)

# Track events - triggers matching workflows
fbf.track("course.abandoned", {
    "user_id": "u_123",
    "course_id": "course_456",
    "course_name": "Python Basics",
    "progress": 35,
    "last_active_at": "2025-02-10T10:00:00Z",
})

# Send user context - helps optimize delivery
fbf.notify({
    "user_id": "u_123",
    "timezone": "Asia/Kolkata",
    "learning_style": "visual",
})
```

## Events Reference

| Event | When to Track | Triggers |
|-------|---------------|----------|
| `course.enrolled` | User enrolls in a course | Welcome & onboarding workflow |
| `course.abandoned` | User inactive for 7+ days mid-course | Course re-engagement workflow |
| `streak.broken` | User misses a day, breaking their streak | Streak recovery workflow |
| `certificate.earned` | User completes a course | Celebration & upsell workflow |
| `level.completed` | User completes a module/lesson | Progress milestone workflow |

## License

MIT
