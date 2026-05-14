"""
Central configuration: keywords, filters, and scraper settings.
Tailored job search.
"""

# ─── Target Job Title Keywords ────────────────────────────────────────────────
# A job title must CONTAIN at least one of these (case-insensitive) to be included.
TITLE_KEYWORDS = [
    "entry-level",
    "entry level",
    "associate",
    "junior",
]

# ─── Technical Skills Keywords ────────────────────────────────────────────────
# Used to boost relevance score when found in job description.
SKILL_KEYWORDS = [
    "python", "sql", "java", "linux", "data analysis",
    "qa", "quality assurance", "agile", "scrum", "tableau",
    "power bi", "database", "pytest", "html", "css", "crm", "jira",
    "algorithms", "data structures", "api", "rest", "json",
]

# ─── Seniority Filters ────────────────────────────────────────────────────────
# INCLUDE jobs that have at least one of these (or no seniority restriction at all)
SENIORITY_INCLUDE = [
    "entry level", "entry-level", "associate", "junior",
    "new grad", "0-2 years", "1-2 years", "1+ year", "2+ years",
    "mid level", "mid-level",  # include mid-level since i have relevant experience
]

# EXCLUDE jobs where title or description contains these
SENIORITY_EXCLUDE = [
    "senior", "sr.", "staff", "principal", "director",
    "vp ", "vice president", "head of", "lead", "manager of",
    "5+ years", "6+ years", "7+ years", "8+ years", "10+ years",
]

# ─── Location Filter ──────────────────────────────────────────────────────────
LOCATION_INCLUDE = [
    "new york", "nyc", ", ny", "ny,", "(ny)", "new york city",
    "remote",  # include remote roles (US-based startups)
    "hybrid",  # include hybrid roles
]

# ─── Scraper Settings ─────────────────────────────────────────────────────────
COMPANY_DB_URL = "https://www.israelimappedinny.com/database"
COMPANY_DB_PAGE_PARAM = "75ad698b_page"  # query param for pagination

# Common careers page URL patterns to try per company
CAREERS_PATH_GUESSES = [
    "/careers",
    "/jobs",
    "/our-careers",
    "/open-positions",
    "/work-with-us",
    "/join-us",
    "/join",
    "/open-roles",
    "/openings",
    "/about/careers",
    "/company/careers",
    "/en/careers",
    "/career-opportunities",
    "/people",
    "/work",
    "/team",
]

# Known ATS platforms and their URL patterns
ATS_PATTERNS = {
    "greenhouse": ["boards.greenhouse.io", "job-boards.greenhouse.io"],
    "lever": ["jobs.lever.co"],
    "ashby": ["jobs.ashbyhq.com"],
    "workday": ["myworkdayjobs.com", "wd1.myworkdayjobs.com", "wd3.myworkdayjobs.com"],
}

# Concurrency settings
MAX_WORKERS = 3          # balanced for stability and speed
REQUEST_TIMEOUT = 10      # seconds per HTTP request
REQUEST_DELAY = 0.5       # seconds between requests to same domain
MAX_PAGES_PER_DB = 30     # safety cap on company DB pages

# User agent to avoid bot detection
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
