import json

from app.agents.scraper import scrape_website
from app.services.ollama import ask_qwen
from app.agents.qualification import qualify_company
from app.agents.signals import clean_signals

from app.database.database import (
    initialize_database,
    save_company,
    save_signals,
    save_qualification
)


def analyze_company(url: str):

    # ============================================================
    # INITIALIZE DATABASE
    # ============================================================

    initialize_database()

    # ============================================================
    # 1. SCRAPE COMPANY WEBSITE
    # ============================================================

    print(f"\nAnalyzing: {url}")
    print("\nScraping website...\n")

    result = scrape_website(url)

    if not result.get("success"):
        raise RuntimeError(
            f"Website scraping failed: {result.get('error', 'Unknown error')}"
        )

    print("Website scraped successfully.")
    print("Title:", result.get("title", ""))

    # ============================================================
    # 2. ASK QWEN TO FIND GTM SIGNALS
    # ============================================================

    prompt = f"""
You are a strict Go-To-Market (GTM) signal intelligence analyst.

IMPORTANT:
GTM means Go-To-Market, NOT Google Tag Manager.

Your job is to identify REAL business events from the provided
company website text.

CRITICAL PRINCIPLE:

A website listing is NOT automatically a business event.

You must distinguish between:

1. REAL BUSINESS EVENTS
2. STATIC WEBSITE INFORMATION

Only REAL BUSINESS EVENTS can become signals.

--------------------------------------------------
VALID SIGNAL RULES
--------------------------------------------------

A signal must describe something that actually happened.

Valid examples:

- A product was launched
- A product was released
- A company announced funding
- A company announced a partnership
- A company announced expansion into a market
- A company announced a leadership change
- A company announced a hiring/growth event
- A company announced a pricing change
- A company announced a major technology change

--------------------------------------------------
PRODUCT LAUNCH RULE
--------------------------------------------------

A product is a product_launch ONLY when the source explicitly
indicates that it was launched, released, introduced, announced,
unveiled, or became available.

VALID:

"Introducing Fable 5.1 and Mythos 5.1"

INVALID:

"Products: Claude Code, Claude Design, Claude Science"

The second example is only a product listing.

Do NOT convert a product menu into a product launch.

--------------------------------------------------
MARKET EXPANSION RULE
--------------------------------------------------

A market_expansion signal requires explicit evidence that the
company expanded, entered, launched in, or announced expansion
into a market, geography, or industry.

INVALID:

"Solutions: Healthcare, Government, Finance, Legal"

This is only a list of solutions.

Do NOT convert a list of industries into a market expansion signal.

--------------------------------------------------
HIRING RULE
--------------------------------------------------

A hiring signal requires explicit evidence such as:

- hiring
- recruiting
- workforce growth
- headcount increase
- hiring plans
- job expansion

A careers page by itself is NOT a hiring signal.

--------------------------------------------------
PARTNERSHIP RULE
--------------------------------------------------

A partnership signal requires explicit language such as:

- partnered with
- partnership with
- strategic partnership
- collaboration with
- announced partnership

A company merely mentioning another company is NOT enough.

--------------------------------------------------
FUNDING RULE
--------------------------------------------------

A funding signal requires explicit evidence of:

- funding
- investment
- fundraising
- funding round
- Series A/B/C/etc.
- raised money

--------------------------------------------------
LEADERSHIP RULE
--------------------------------------------------

A leadership signal requires explicit evidence of:

- appointed
- hired
- promoted
- joined as CEO/CFO/CTO/etc.
- leadership change

--------------------------------------------------
TECHNOLOGY CHANGE RULE
--------------------------------------------------

A technology_change signal requires an explicit technology
announcement or change.

Do NOT classify normal product descriptions as technology changes.

--------------------------------------------------
EVIDENCE RULE
--------------------------------------------------

Every signal MUST have direct evidence from the supplied text.

The evidence must support the exact event.

Do NOT infer an event from:

- navigation menus
- product menus
- solution lists
- industry lists
- category pages
- footer links
- generic marketing text
- website navigation
- product names alone

--------------------------------------------------
NO GUESSING
--------------------------------------------------

Use ONLY the provided text.

Do NOT use outside knowledge.

Do NOT assume something happened.

Do NOT turn implications into facts.

If the text does not provide enough evidence,
DO NOT create a signal.

It is better to return ZERO signals than a false signal.

--------------------------------------------------
SIGNAL LIMIT
--------------------------------------------------

Return a MAXIMUM of 5 signals.

Only return distinct, meaningful business events.

Do not create multiple signals for the same event.

Prefer recent and high-impact events.

--------------------------------------------------
STRENGTH
--------------------------------------------------

Strength must be between 0 and 100.

Use:

90-100 = very strong explicit business event
75-89  = strong explicit business event
60-74  = moderate explicit business event
below 60 = usually do not include

Do NOT give a high score to weak or inferred signals.

--------------------------------------------------
JSON RULES
--------------------------------------------------

Return ONLY valid JSON.

Do NOT use Markdown.

Do NOT use ```json.

Return ONE JSON object.

Do NOT put line breaks inside string values.

Use exactly this structure:

{{
  "company": "company name",
  "signals": [
    {{
      "type": "product_launch",
      "event": "what actually happened",
      "why_it_matters": "why this business event matters",
      "evidence": "supporting evidence from the provided text",
      "strength": 0
    }}
  ]
}}

Allowed signal types:

- product_launch
- hiring
- funding
- market_expansion
- partnership
- leadership_change
- technology_change
- pricing_change
- sales_expansion
- marketing_expansion

Company website:
{url}

Company information:
{result["text"][:4000]}
"""

    # ============================================================
    # 3. RUN QWEN
    # ============================================================

    print("\nAnalyzing GTM signals with Qwen...\n")

    analysis = ask_qwen(prompt)

    print("RAW SIGNAL ANALYSIS:")
    print(analysis)

    # ============================================================
    # 4. PARSE QWEN JSON
    # ============================================================

    try:
        clean = analysis.strip()

        clean = clean.replace("```json", "")
        clean = clean.replace("```", "")
        clean = clean.strip()

        start = clean.find("{")
        end = clean.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found")

        json_text = clean[start:end]

        signal_data = json.loads(
            json_text,
            strict=False
        )

    except (json.JSONDecodeError, ValueError) as e:

        print("\nERROR: Could not extract valid JSON from Qwen.")
        print("Reason:", e)
        print("\nQwen response:")
        print(analysis)

        raise RuntimeError(
            "Qwen returned invalid signal JSON."
        )

    # ============================================================
    # 5. CLEAN AND FILTER SIGNALS
    # ============================================================

    company = signal_data.get(
        "company",
        "Unknown"
    )

    signals = signal_data.get(
        "signals",
        []
    )

    signals = clean_signals(signals)

    print("\nNumber of signals:", len(signals))

    # ============================================================
    # 6. DISPLAY GTM SIGNALS
    # ============================================================

    print("\nGTM SIGNALS:")

    for i, signal in enumerate(
        signals,
        start=1
    ):

        print(f"\nSignal {i}")

        print(
            "Type:",
            signal.get("type")
        )

        print(
            "Event:",
            signal.get("event")
        )

        print(
            "Why it matters:",
            signal.get("why_it_matters")
        )

        print(
            "Evidence:",
            signal.get("evidence")
        )

        print(
            "Strength:",
            signal.get("strength")
        )

    # ============================================================
    # 7. SAVE COMPANY
    # ============================================================

    company_id = save_company(
        company,
        url
    )

    print("\nCompany saved successfully.")

    # ============================================================
    # 8. SAVE SIGNALS
    # ============================================================

    save_signals(
        company_id,
        signals
    )

    print("Signals saved successfully.")

    # ============================================================
    # 9. QUALIFY COMPANY
    # ============================================================

    print("\nRunning Qualification Agent...\n")

    qualification = qualify_company(
        company,
        signals
    )

    # ============================================================
    # 10. SAVE QUALIFICATION
    # ============================================================

    save_qualification(
        company_id,
        qualification
    )

    print("Qualification saved successfully.")

    # ============================================================
    # RETURN RESULTS
    # ============================================================

    return {
        "company_id": company_id,
        "company": company,
        "website": url,
        "signals": signals,
        "qualification": qualification
    }


# ============================================================
# RUN DIRECTLY FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    url = "https://www.anthropic.com/"

    result = analyze_company(url)

    print("\nQUALIFICATION RESULT:")

    print(
        json.dumps(
            result["qualification"],
            indent=2
        )
    )

    print("\nPipeline completed.")