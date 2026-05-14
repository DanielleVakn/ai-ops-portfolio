"""
Filter logic for job listings.
Filters by location (New York), title keywords, and seniority.
Also scores jobs by relevance to Danielle's profile.
"""

from config import (
    TITLE_KEYWORDS, SKILL_KEYWORDS,
    SENIORITY_INCLUDE, SENIORITY_EXCLUDE,
    LOCATION_INCLUDE,
)


def filter_jobs(jobs: list[dict]) -> list[dict]:
    """
    Main filter pipeline. Returns filtered + scored jobs, sorted by relevance.
    Each job dict must have: title, location, url, description, department
    """
    filtered = []
    for job in jobs:
        title = job.get("title", "").lower()
        location = job.get("location", "").lower()
        description = job.get("description", "").lower()
        department = job.get("department", "").lower()

        # Must pass location filter
        if not _passes_location(job):
            continue

        # Must match at least one title keyword
        if not _matches_title(title, department):
            continue

        # Must not be excluded by seniority
        if _is_senior_only(title, description):
            continue

        # Score the job
        score = _score_job(title, description, department)
        job["relevance_score"] = score
        job["seniority_level"] = _classify_seniority(title, description)

        filtered.append(job)

    # Sort by relevance score descending
    filtered.sort(key=lambda j: j.get("relevance_score", 0), reverse=True)
    return filtered


def _passes_location(job: dict) -> bool:
    """Check if job is in New York or remote."""
    title = job.get("title", "").lower()
    location = job.get("location", "").lower()
    description = job.get("description", "").lower()
    url = job.get("url", "").lower()
    
    combined = f"{location} {title} {url} {description[:300]}"
    for loc in LOCATION_INCLUDE:
        if loc in combined:
            return True
    return False


def _matches_title(title: str, department: str = "") -> bool:
    """Check if job title matches any target keyword."""
    combined = f"{title} {department}".lower()
    for kw in TITLE_KEYWORDS:
        if kw.lower() in combined:
            return True
    return False


def _is_senior_only(title: str, description: str) -> bool:
    """Return True if this job is clearly for senior candidates only."""
    combined = f"{title} {description[:500]}"
    for exclusion in SENIORITY_EXCLUDE:
        if exclusion in combined:
            # But don't exclude if there's an explicit entry-level signal too
            for include in SENIORITY_INCLUDE:
                if include in combined:
                    return False  # conflicting signals → keep it
            return True
    return False


def _score_job(title: str, description: str, department: str) -> int:
    """Score job relevance: 0-100. Higher = better match."""
    score = 0
    combined = f"{title} {description} {department}"

    # Title match quality
    for kw in TITLE_KEYWORDS:
        if kw in title:
            score += 20  # strong signal: keyword in title
        elif kw in combined:
            score += 5   # weaker signal: keyword in description

    # Skill keyword matches
    for skill in SKILL_KEYWORDS:
        if skill in description:
            score += 3

    # Seniority bonuses
    for inc in SENIORITY_INCLUDE:
        if inc in combined:
            score += 10
            break

    # NYC specifically is better than just "remote"
    if "new york" in combined or "nyc" in combined:
        score += 10
    elif "remote" in combined:
        score += 3

    return min(score, 100)


def _classify_seniority(title: str, description: str) -> str:
    """Return a human-readable seniority classification."""
    combined = f"{title} {description[:300]}"
    for inc in SENIORITY_INCLUDE:
        if inc in combined:
            if "junior" in combined:
                return "Junior"
            if "associate" in combined:
                return "Associate"
            if "entry" in combined or "new grad" in combined:
                return "Entry Level"
            return "Early Career"
    return "Unspecified"
