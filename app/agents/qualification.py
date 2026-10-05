import json
import re

from app.services.ollama import ask_qwen


def qualify_company(company: str, signals: list) -> dict:

    signals_text = json.dumps(
        signals,
        indent=2
    )

    prompt = f"""
You are a strict B2B Go-To-Market qualification agent.

Your job is to score a company using ONLY the provided signals.

Company:
{company}

Signals:
{signals_text}

==================================================
SCORING DEFINITIONS
==================================================

ICP FIT:
How well the company appears to match the target customer profile.

OPPORTUNITY SCORE:
How commercially valuable the company could potentially be.

BUYING INTENT:
IMPORTANT:
Buying intent means evidence that the company is actively looking
for a solution, vendor, service, technology, partnership, or similar
business need.

Product launches alone are NOT buying intent.

Examples of LOW buying intent:

- launching a new product
- releasing a new model
- improving product performance
- announcing a new feature

Examples of HIGH buying intent:

- hiring specifically for a problem our product solves
- publicly searching for vendors
- announcing an initiative requiring external technology
- requesting partnerships
- announcing expansion that clearly requires a relevant solution
- publishing a request for proposals
- actively evaluating or adopting a relevant technology

If there is NO direct evidence of buying intent,
buying_intent MUST be between 0 and 30.

Do NOT infer buying intent from general company growth.

SIGNAL STRENGTH:
How strong and reliable the supplied business signals are.

==================================================
IMPORTANT RULE
==================================================

Never confuse:

BUSINESS ACTIVITY

with

BUYING INTENT.

A company can have extremely strong business activity
without having buying intent.

==================================================
SCORING
==================================================

All scores must be between 0 and 100.

Use these guidelines:

ICP FIT:
0-30   = poor fit
31-60  = uncertain
61-80  = good fit
81-100 = excellent fit

OPPORTUNITY:
0-30   = low opportunity
31-60  = moderate
61-80  = strong
81-100 = very strong

BUYING INTENT:
0-30   = no direct buying evidence
31-60  = some evidence
61-80  = strong evidence
81-100 = explicit buying activity

SIGNAL STRENGTH:
0-30   = weak
31-60  = moderate
61-80  = strong
81-100 = very strong

==================================================
OVERALL SCORE
==================================================

Calculate overall_score using:

ICP FIT       × 0.25
OPPORTUNITY   × 0.25
BUYING INTENT × 0.25
SIGNAL        × 0.25

Do NOT simply copy the highest score.

==================================================
PRIORITY
==================================================

HIGH:
overall_score >= 75

MEDIUM:
overall_score >= 50 and < 75

LOW:
overall_score < 50

==================================================
REASON
==================================================

Keep the reason short.

Explain the main evidence.

If buying intent is low, explicitly say:

"No direct buying intent detected."

Do not invent facts.

==================================================
JSON RULES
==================================================

Return ONLY valid JSON.

Do NOT use Markdown.

Do NOT use ```json.

Return exactly one JSON object.

Use this structure:

{{
  "company": "{company}",
  "icp_fit": 0,
  "opportunity_score": 0,
  "buying_intent": 0,
  "signal_strength": 0,
  "overall_score": 0,
  "priority": "LOW",
  "reason": "short explanation"
}}
"""

    response = ask_qwen(prompt)

    try:

        clean = re.sub(
            r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])',
            '',
            response
        )

        clean = clean.replace(
            "```json",
            ""
        )

        clean = clean.replace(
            "```",
            ""
        )

        clean = clean.strip()

        start = clean.find("{")
        end = clean.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError(
                "No JSON object found"
            )

        json_text = clean[start:end]

        result = json.loads(
            json_text,
            strict=False
        )

        return result

    except (
        json.JSONDecodeError,
        ValueError
    ):

        return {
            "company": company,
            "error": "Qwen returned invalid JSON",
            "raw_response": response
        }