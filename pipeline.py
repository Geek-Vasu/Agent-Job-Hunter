import sys
import subprocess
import json
import re
from agents.analyst import rank_jobs
from agents.tailor import tailor_application


def extract_json_array(text: str):
    """
    Extract first valid JSON array from noisy logs.
    """
    match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
    if not match:
        return None
    return match.group(0)


def run_agent(query: str):

    # ==========================================
    # STEP 1 — SCOUT (subprocess safe mode)
    # ==========================================
    try:
        process = subprocess.run(
            [sys.executable, "agents/scout.py", query],
            capture_output=True,
            text=True,
            check=True
        )

        raw_output = process.stdout.strip()

        json_block = extract_json_array(raw_output)

        if not json_block:
            raise RuntimeError(f"Could not extract JSON from Scout:\n{raw_output}")

        jobs = json.loads(json_block)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Scout process failed:\n{e.stderr}")

    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON returned from Scout:\n{raw_output}")

    if not jobs:
        raise RuntimeError("No jobs found.")

    # ==========================================
    # STEP 2 — ANALYST
    # ==========================================
    ranked_jobs = rank_jobs(jobs, query)

    if not ranked_jobs:
        raise RuntimeError("Ranking failed.")

    best_match = ranked_jobs[0]
    alternatives = ranked_jobs[1:3]

    # ==========================================
    # STEP 3 — TAILOR
    # ==========================================
    tailored_package = tailor_application(best_match, query)

    return {
        "best_match": best_match,
        "tailored_package": tailored_package,
        "alternatives": alternatives
    }


if __name__ == "__main__":
    result = run_agent("Machine Learning Intern")
    print(json.dumps(result, indent=2))
