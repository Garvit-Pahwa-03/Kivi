"""Fixed persona + entity universe for the synthetic corpus.
Keeping this centralized means the eval question set and the corpus
generator always agree on ground truth.
"""

USER_NAME = "Priya Menon"
COMPANY = "Loopwork"

TEAMMATES = [
    {"name": "Rahul Iyer", "role": "Engineering Lead"},
    {"name": "Ananya Rao", "role": "Design Lead"},
    {"name": "Vikram Shah", "role": "Backend Engineer"},
    {"name": "Divya Nair", "role": "Growth Analyst"},
]

TEAMS = ["Growth Pod", "Platform Pod"]

PROJECTS = [
    {"name": "Project Falcon", "acronym": "PRJ-FLC", "desc": "the new onboarding flow redesign"},
    {"name": "Project Comet", "acronym": "PRJ-CMT", "desc": "the billing system migration"},
]

CLIENTS = ["Northwind Traders", "Meridian Retail"]

APPS = ["Slack", "Google Docs", "Outlook", "Notes"]

# Ground-truth facts the corpus deliberately encodes, for the eval set to check against.
KNOWN_FACTS = {
    "PRJ-FLC": "Project Falcon, the new onboarding flow redesign",
    "PRJ-CMT": "Project Comet, the billing system migration",
    "Rahul Iyer": "Engineering Lead",
    "Ananya Rao": "Design Lead",
    "Vikram Shah": "Backend Engineer",
    "Divya Nair": "Growth Analyst",
}

# Deliberately NEVER mentioned anywhere in the corpus — used for abstention tests.
UNKNOWN_ENTITIES = ["Project Nimbus", "PRJ-NMB", "Karan Bose"]