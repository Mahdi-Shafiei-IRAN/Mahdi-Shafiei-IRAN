import pytest


@pytest.fixture
def profile_raw() -> dict:
    return {
        "name": "Mahdi Shafiei",
        "username": "Mahdi-Shafiei-IRAN",
        "role": "Computer Engineering Student · Python & Django Developer",
        "tagline": "Coding since 14 — writing, making videos, always learning.",
        "location": "Iran",
        "about": "A computer engineering student who loves building things.",
        "learning": ["Django", "Python"],
        "skills": ["Python", "Django", "Django REST", "Docker", "Git", "Linux", "PostgreSQL", "C#"],
        "education": {"degree": "B.Sc. Computer Engineering", "university": "Example University"},
        "links": {
            "linkedin": "https://linkedin.com/in/mahdi-shafiei-iran",
            "email": "me@example.com",
        },
    }
