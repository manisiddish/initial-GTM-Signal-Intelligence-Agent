import json
import re

from app.services.ollama import ask_qwen


# ============================================================
# CLEAN RESPONSE
# ============================================================

def clean_response(response: str) -> str:

    if not response:
        return ""

    # Remove ANSI terminal escape sequences
    response = re.sub(
        r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])",
        "",
        response,
    )

    # Remove <think>...</think> blocks if Qwen produces them
    response = re.sub(
        r"<think>.*?</think>",
        "",
        response,
        flags=re.DOTALL,
    )

    # Remove markdown fences
    response = response.replace("```json", "")
    response = response.replace("```", "")

    # Remove control characters
    cleaned = ""

    for char in response:

        if char in "\n\r\t":
            cleaned += char

        elif ord(char) >= 32:
            cleaned += char

    return cleaned.strip()


# ============================================================
# PARSE JSON
# ============================================================

def parse_outreach_response(response: str):

    cleaned = clean_response(response)

    # --------------------------------------------------------
    # Method 1: Normal JSON parsing
    # --------------------------------------------------------

    try:

        data = json.loads(cleaned)

        if isinstance(data, dict):
            return data

    except Exception:
        pass


    # --------------------------------------------------------
    # Method 2: Find JSON object inside response
    # --------------------------------------------------------

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = cleaned[
            start:end + 1
        ]

        try:

            data = json.loads(
                json_text
            )

            if isinstance(data, dict):
                return data

        except Exception:
            pass


    # --------------------------------------------------------
    # Method 3: Extract fields manually
    # --------------------------------------------------------

    subject_match = re.search(
        r'"email_subject"\s*:\s*"((?:\\.|[^"\\])*)"',
        cleaned,
        re.DOTALL,
    )

    body_match = re.search(
        r'"email_body"\s*:\s*"((?:\\.|[^"\\])*)"',
        cleaned,
        re.DOTALL,
    )

    linkedin_match = re.search(
        r'"linkedin_message"\s*:\s*"((?:\\.|[^"\\])*)"',
        cleaned,
        re.DOTALL,
    )


    if (
        subject_match
        or body_match
        or linkedin_match
    ):

        def decode(value):

            if not value:
                return ""

            try:
                return json.loads(
                    '"' + value + '"'
                )

            except Exception:
                return value


        return {
            "email_subject": decode(
                subject_match.group(1)
                if subject_match
                else ""
            ),

            "email_body": decode(
                body_match.group(1)
                if body_match
                else ""
            ),

            "linkedin_message": decode(
                linkedin_match.group(1)
                if linkedin_match
                else ""
            ),
        }


    # Nothing worked
    raise ValueError(
        "Could not extract outreach fields from Qwen response."
    )


# ============================================================
# GENERATE OUTREACH
# ============================================================

def generate_outreach(
    company: str,
    signals: list,
    qualification: dict
):

    prompt = f"""
You are a professional B2B sales outreach assistant.

Create personalized outreach for the company below.

COMPANY:
{company}

DETECTED GTM SIGNALS:
{json.dumps(signals, indent=2, ensure_ascii=False)}

QUALIFICATION:
{json.dumps(qualification, indent=2, ensure_ascii=False)}

RULES:

1. Use ONLY the information provided above.
2. Do not invent facts.
3. Do not claim the company is looking for vendors
   unless the signals explicitly indicate buying intent.
4. Mention relevant business signals naturally.
5. Keep the email concise and professional.
6. Keep the LinkedIn message short.
7. Do not mention AI.
8. Do not mention qualification scores.
9. Do not use markdown.
10. Return ONLY one valid JSON object.
11. Do not write anything before or after the JSON.

The JSON MUST have exactly these three fields:

{{
  "email_subject": "short personalized subject",
  "email_body": "professional personalized email",
  "linkedin_message": "short personalized LinkedIn message"
}}
"""


    response = ""


    try:

        # Call Qwen
        response = ask_qwen(prompt)

        # Parse response
        result = parse_outreach_response(
            response
        )


        # ----------------------------------------------------
        # Make sure fields exist
        # ----------------------------------------------------

        return {
            "email_subject": result.get(
                "email_subject",
                ""
            ),

            "email_body": result.get(
                "email_body",
                ""
            ),

            "linkedin_message": result.get(
                "linkedin_message",
                ""
            ),
        }


    except Exception as e:

        return {
            "error": "Could not parse outreach response",

            "details": str(e),

            "raw_response": response,
        }