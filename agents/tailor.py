from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RESUME_PATH = DATA_DIR / "master_resume.md"


def tailor_application(job: dict, user_query: str):
    """
    job = {
        "title": "...",
        "company": "...",
        "description": "...",
        "source_url": "..."
    }
    """

    if not RESUME_PATH.exists():
        raise FileNotFoundError("master_resume.md not found in data folder.")

    resume_text = RESUME_PATH.read_text(encoding="utf-8")

    prompt = f"""
You are an AI Career Strategy Assistant.

Your job is to analyze:

1) Candidate Resume
2) Job Description
3) User Search Intent

And generate structured output.

DO NOT fabricate experience.
DO NOT invent skills not mentioned in resume.
You may identify missing skills separately.

----------------------------------------
USER SEARCH QUERY:
{user_query}

----------------------------------------
JOB TITLE:
{job['title']}

COMPANY:
{job['company']}

JOB DESCRIPTION:
{job['description']}

----------------------------------------
CANDIDATE RESUME:
{resume_text}

----------------------------------------

OUTPUT REQUIREMENTS:

Return ONLY valid JSON.

Format:

{{
  "skill_gap_analysis": {{
      "missing_skills": [],
      "priority_levels": {{
          "high": [],
          "medium": [],
          "low": []
      }},
      "learning_recommendations": []
  }},
  "cold_email": {{ 
    "subject": "",
    "body": ""
   }},

  "tailored_summary": "",
  "skill_emphasis_suggestions": []
}}

INSTRUCTIONS:

1. Skill Gap:
   - Compare JD vs Resume.
   - Identify missing technical skills.
   - Prioritize realistically.
   - Suggest practical learning directions.

2. Cold Email:
   - Professional.
   - 150–200 words.
   - Mention company name.
   - Reference 1–2 relevant resume projects.
   - Show genuine interest.
   - No exaggeration.


3. Generate a technically strong professional summary:
   - 2–3 lines
   - System-level thinking
   - Production-oriented ML
   - No student fluff
   - Confident tone


4. Skill Emphasis Suggestions:
   - List which existing resume skills should be highlighted.
   - No new invented skills.

Return JSON only.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a precise structured-output generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content.strip()

# Remove markdown fences if present
    if raw_output.startswith("```"):
       raw_output = raw_output.strip("```")
       raw_output = raw_output.replace("json", "").strip()

# Try extracting JSON block manually
    import re
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)

    if not match:
       raise RuntimeError("No JSON object found in LLM output.")

    json_text = match.group(0)

    try:
       result = json.loads(json_text)
    except json.JSONDecodeError as e:
       print("⚠ Raw LLM Output:\n")
       print(raw_output)
       raise RuntimeError("Tailor LLM returned malformed JSON.")

    return result


    


# Optional standalone test
if __name__ == "__main__":
    sample_job = {
        "title": "Machine Learning Intern",
        "company": "Example AI",
        "description": "Looking for interns with ML, Python, TensorFlow, and NLP experience.",
        "source_url": "https://example.com"
    }

    result = tailor_application(sample_job, "Remote Machine Learning Intern")

    print(json.dumps(result, indent=2))
