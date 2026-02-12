import sys
import asyncio
import json
from browser_use import Agent
from dotenv import load_dotenv

load_dotenv()


# -----------------------------------------
# CORE SCOUT LOGIC
# -----------------------------------------
async def scout_jobs(query: str, max_jobs: int = 3):

    # -----------------------------------------
    # Extract clean technical keyword
    # -----------------------------------------
    if "machine learning" in query.lower():
        search_keyword = "Machine Learning"
    elif "data science" in query.lower():
        search_keyword = "Data Science"
    elif "backend" in query.lower():
        search_keyword = "Backend"
    elif "ai" in query.lower():
        search_keyword = "Artificial Intelligence"
    else:
        search_keyword = query.strip()

    # -----------------------------------------
    # Deterministic prompt
    # -----------------------------------------
    task_prompt = f"""
You are a deterministic job scouting agent.

Target website: Internshala

GOAL:
Find up to {max_jobs} internships matching: "{search_keyword}"

POPUP HANDLING:
After clicking "Internships":
- Immediately close sign-up popup if visible.
- Do NOT read it.
- Do NOT scroll before closing.

SEARCH RULES:
1. Open https://internshala.com
2. Click "Internships"
3. Close popup
4. Use ONLY main keyword search bar
5. Type EXACTLY "{search_keyword}"
6. Press Enter
7. Do NOT use filters
8. Collect first {max_jobs} relevant internships only

FOR EACH:
- Click job title
- Extract:
    - title
    - company
    - full description
    - source_url (current URL)
- Return to results page

OUTPUT:
Return ONLY valid JSON list.
No markdown.
No commentary.

Format:
[
  {{
    "title": "...",
    "company": "...",
    "description": "...",
    "source_url": "..."
  }}
]
"""

    agent = Agent(
        task=task_prompt,
        provider="browser-use",
        model="bu-3.0")
    result = await agent.run()

    raw_text = result.final_result() if callable(result.final_result) else result.final_result

    if not raw_text:
        raise RuntimeError("Scout did not return final result.")

    raw_text = raw_text.strip()

    # Remove markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    # Handle escaped JSON
    if '\\"' in raw_text:
        raw_text = raw_text.encode("utf-8").decode("unicode_escape")

    try:
        jobs = json.loads(raw_text)

        # Handle double-encoded JSON
        if isinstance(jobs, str):
            jobs = json.loads(jobs)

    except json.JSONDecodeError:
        print("⚠ Raw Scout Output:\n", raw_text)
        raise RuntimeError("Scout returned malformed JSON.")

    if not isinstance(jobs, list):
        raise RuntimeError("Scout output is not a list.")

    return jobs


# -----------------------------------------
# CLI ENTRYPOINT (CRITICAL FOR STREAMLIT)
# -----------------------------------------
if __name__ == "__main__":

    # Read query from command line
    query = sys.argv[1] if len(sys.argv) > 1 else "Machine Learning Intern"

    try:
        jobs = asyncio.run(scout_jobs(query))
        print(json.dumps(jobs))  # IMPORTANT: Only JSON output
    except Exception as e:
        print(str(e))
        sys.exit(1)
