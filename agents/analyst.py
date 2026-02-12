from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESUME_PATH = DATA_DIR / "master_resume.md"


def rank_jobs(jobs: list, user_query: str):
    """
    Takes list of job dicts
    Returns sorted jobs with match_score
    """

    if not RESUME_PATH.exists():
        raise FileNotFoundError("master_resume.md not found.")

    resume_text = RESUME_PATH.read_text(encoding="utf-8")

    prompt = f"""
You are an AI job fit evaluator.

Given:
1) User search query
2) Candidate resume
3) Multiple job descriptions

Score each job from 0–100 based on:
- Skill match
- Relevance to query
- Career alignment
- Internship suitability

Return ONLY valid JSON array.

Format:
[
  {{
    "title": "...",
    "company": "...",
    "description": "...",
    "source_url": "...",
    "match_score": number,
    "reason": "short explanation"
  }}
]

------------------------------------

USER QUERY:
{user_query}

------------------------------------

CANDIDATE RESUME:
{resume_text}

------------------------------------

JOBS:
{json.dumps(jobs, indent=2)}

------------------------------------

Return sorted highest match_score first.
Return JSON only.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Return structured JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw = response.choices[0].message.content.strip()

    # robust extraction
    import re
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise RuntimeError("Analyst did not return JSON.")

    json_text = match.group(0)

    try:
        ranked = json.loads(json_text)
    except json.JSONDecodeError:
        print("Raw Analyst Output:\n", raw)
        raise RuntimeError("Failed to parse analyst JSON.")

    return ranked
