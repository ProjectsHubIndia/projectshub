# AI ProjectsHub — Django Backend

This is the full Django backend added to the AI frontend project.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data         # Optional: populate sample data
python manage.py createsuperuser   # Create admin login
python manage.py runserver
```

## URL Routes

| URL | View |
|-----|------|
| `/` | Homepage (index) |
| `/projects/` | All projects |
| `/projects/<id>/` | Project detail |
| `/workshop/` | Workshop page |
| `/admin/` | Django admin |

## API Endpoints (JSON)

| URL | Description |
|-----|-------------|
| `GET /api/projects/` | All active projects |
| `GET /api/projects/?index_only=1` | Homepage projects only |
| `GET /api/pricing/` | Pricing plans + features |
| `GET /api/workshops/` | Workshops + days |

## Form Endpoints (POST)

| URL | Model |
|-----|-------|
| `POST /contact/` | `ContactMessage` |
| `POST /gate/` | `ProjectGateLead` |
| `POST /idea/` | `IdeaSubmission` |
| `POST /enroll/` | `WorkshopEnrollment` |

## Database Models

| Model | Table | Purpose |
|-------|-------|---------|
| `Project` | `core_project` | Project cards (index + projects page) |
| `WorkshopCard` | `core_workshopcard` | Workshop listings |
| `WorkshopDay` | `core_workshopday` | Per-day curriculum |
| `PricingPlan` | `core_pricingplan` | Pricing tiers |
| `PricingFeature` | `core_pricingfeature` | Plan feature bullets |
| `ContactMessage` | `core_contactmessage` | Contact form submissions |
| `ProjectGateLead` | `core_projectgatelead` | Gate modal leads |
| `IdeaSubmission` | `core_ideasubmission` | "Share Your Idea" modal |
| `WorkshopEnrollment` | `core_workshopenrollment` | Workshop enrollments |

## Admin

All models are registered in Django Admin at `/admin/`.
- Manage projects, workshops, pricing from the admin panel
- View all form submissions (contact, gate leads, ideas, enrollments)
- Status tracking for messages and submissions
