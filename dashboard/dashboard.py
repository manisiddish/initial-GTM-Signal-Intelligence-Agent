import sys
import sqlite3
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from app.main import analyze_company
from app.agents.scraper import scrape_website
from app.agents.outReach import generate_outreach
from app.services.email import send_email


# ============================================================
# DATABASE
# ============================================================

DB_PATH = PROJECT_ROOT / "data" / "gtm_signals.db"


def get_connection():

    return sqlite3.connect(DB_PATH)


# ============================================================
# GET COMPANIES
# ============================================================

def get_companies():

    conn = get_connection()

    try:

        query = """
        SELECT DISTINCT
            c.id,
            c.name,
            c.website
        FROM companies c
        LEFT JOIN signals s
            ON c.id = s.company_id
        ORDER BY c.name
        """

        rows = conn.execute(
            query
        ).fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "website": row[2],
            }
            for row in rows
        ]

    finally:

        conn.close()


# ============================================================
# GET SIGNALS
# ============================================================

def get_signals(company_id):

    conn = get_connection()

    try:

        query = """
        SELECT
            signal_type,
            event,
            why_it_matters,
            evidence,
            strength,
            created_at
        FROM signals
        WHERE company_id = ?
        ORDER BY created_at DESC
        """

        rows = conn.execute(
            query,
            (company_id,)
        ).fetchall()

        return [
            {
                "signal_type": row[0],
                "event": row[1],
                "why_it_matters": row[2],
                "evidence": row[3],
                "strength": row[4],
                "created_at": row[5],
            }
            for row in rows
        ]

    finally:

        conn.close()


# ============================================================
# GET QUALIFICATION
# ============================================================

def get_qualification(company_id):

    conn = get_connection()

    try:

        columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(qualifications)"
            ).fetchall()
        ]

        if not columns:
            return None

        if "company_id" in columns:

            query = """
            SELECT *
            FROM qualifications
            WHERE company_id = ?
            ORDER BY rowid DESC
            LIMIT 1
            """

            row = conn.execute(
                query,
                (company_id,)
            ).fetchone()

        elif "company" in columns:

            company_row = conn.execute(
                """
                SELECT name
                FROM companies
                WHERE id = ?
                """,
                (company_id,)
            ).fetchone()

            if not company_row:
                return None

            row = conn.execute(
                """
                SELECT *
                FROM qualifications
                WHERE company = ?
                ORDER BY rowid DESC
                LIMIT 1
                """,
                (company_row[0],)
            ).fetchone()

        else:

            return None

        if not row:
            return None

        return dict(
            zip(columns, row)
        )

    except sqlite3.OperationalError:

        return None

    finally:

        conn.close()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GTM Signal Intelligence",
    page_icon="🎯",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
    }

    .hero {
        padding: 25px;
        border-radius: 15px;
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        margin-bottom: 5px;
    }

    .hero p {
        color: #d1d5db;
        margin-top: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🎯 GTM Signal Intelligence</h1>
        <p>
        AI-powered GTM signals, qualification
        and automated personalized outreach.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ANALYZE + AUTO SEND
# ============================================================

st.subheader(
    "🚀 Analyze Company & Send Outreach"
)

st.write(
    "Enter a company website. The system will "
    "find a public business email, detect GTM signals, "
    "qualify the company, generate personalized outreach "
    "and automatically send the email."
)

url_input = st.text_input(
    "Company Website",
    placeholder="https://www.example.com",
)

analyze_send_button = st.button(
    "🚀 Analyze & Send Outreach",
    type="primary",
    use_container_width=True,
)


# ============================================================
# AUTOMATIC PIPELINE
# ============================================================

if analyze_send_button:

    if not url_input.strip():

        st.error(
            "Please enter a company website."
        )

    else:

        url = url_input.strip()

        if not url.startswith(
            ("http://", "https://")
        ):

            url = "https://" + url

        # ----------------------------------------------------
        # STEP 1 — FIND EMAIL
        # ----------------------------------------------------

        with st.spinner(
            "🌐 Scraping website and finding public business email..."
        ):

            email_result = scrape_website(
                url
            )

        if not email_result.get("success"):

            st.error(
                "Website scraping failed: "
                + email_result.get(
                    "error",
                    "Unknown error"
                )
            )

            st.stop()

        recipient_email = email_result.get(
            "email"
        )

        if not recipient_email:

            st.warning(
                "⚠️ No public business email was found "
                "on the website or contact pages."
            )

            st.info(
                "The company was not emailed because "
                "the system does not guess email addresses."
            )

            st.stop()

        st.success(
            f"📧 Public business email found: "
            f"{recipient_email}"
        )

        # ----------------------------------------------------
        # STEP 2 — ANALYZE COMPANY
        # ----------------------------------------------------

        with st.spinner(
            "🤖 Detecting GTM signals and qualifying company..."
        ):

            try:

                analysis_result = analyze_company(
                    url
                )

            except Exception as e:

                st.error(
                    f"Company analysis failed: {e}"
                )

                st.stop()

        company_id = analysis_result["company"]
        company_name = analysis_result["company"]

        # ----------------------------------------------------
        # IMPORTANT:
        # analyze_company currently returns the company name,
        # so we reload the company from the database.
        # ----------------------------------------------------

        companies_now = get_companies()

        selected_company = None

        for item in companies_now:

            if item["name"] == company_name:

                selected_company = item

                break

        if not selected_company:

            st.error(
                "Company was analyzed but could not be loaded "
                "from the database."
            )

            st.stop()

        real_company_id = selected_company["id"]

        signals_now = get_signals(
            real_company_id
        )

        qualification_now = get_qualification(
            real_company_id
        )

        if not signals_now:

            st.warning(
                "No GTM signals were detected. "
                "No outreach email was sent."
            )

            st.stop()

        # ----------------------------------------------------
        # STEP 3 — GENERATE OUTREACH
        # ----------------------------------------------------

        with st.spinner(
            "✍️ Qwen is writing personalized outreach..."
        ):

            outreach_result = generate_outreach(
                company=company_name,
                signals=signals_now,
                qualification=qualification_now or {},
            )

        if "error" in outreach_result:

            st.error(
                outreach_result["error"]
            )

            st.stop()

        email_subject = outreach_result.get(
            "email_subject",
            "Business opportunity"
        )

        email_body = outreach_result.get(
            "email_body",
            ""
        )

        if not email_body.strip():

            st.error(
                "Qwen generated an empty email. "
                "Email was not sent."
            )

            st.stop()

        # ----------------------------------------------------
        # STEP 4 — SEND EMAIL
        # ----------------------------------------------------

        with st.spinner(
            f"📨 Sending outreach to {recipient_email}..."
        ):

            send_result = send_email(
                recipient=recipient_email,
                subject=email_subject,
                body=email_body,
            )

        if send_result.get("success"):

            st.success(
                f"🎉 Outreach sent successfully to "
                f"{recipient_email}"
            )

            # ------------------------------------------------
            # SHOW WHAT WAS SENT
            # ------------------------------------------------

            st.markdown("---")

            st.subheader(
                "📧 Email Sent"
            )

            st.write(
                f"**Company:** {company_name}"
            )

            st.write(
                f"**Recipient:** {recipient_email}"
            )

            st.write(
                f"**Subject:** {email_subject}"
            )

            with st.expander(
                "View sent email"
            ):

                st.text_area(
                    "Email",
                    email_body,
                    height=300,
                )

            st.markdown("---")

            st.subheader(
                "🚨 Detected Signals"
            )

            for signal in signals_now:

                with st.container(
                    border=True
                ):

                    st.write(
                        f"**{signal.get('signal_type')}**"
                    )

                    st.write(
                        signal.get(
                            "event",
                            ""
                        )
                    )

                    st.caption(
                        f"Strength: "
                        f"{signal.get('strength', 0)}/100"
                    )

        else:

            st.error(
                "❌ Email failed: "
                + send_result.get(
                    "error",
                    "Unknown error"
                )
            )


st.markdown("---")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ GTM Intelligence"
)

st.sidebar.markdown(
    """
    **Automatic Pipeline**

    1. 🌐 Find company
    2. 📧 Find public email
    3. 🔎 Detect signals
    4. 📊 Qualify company
    5. ✍️ Generate outreach
    6. 📨 Send automatically
    """
)

st.sidebar.divider()

companies = get_companies()

st.sidebar.metric(
    "Companies detected",
    len(companies),
)

if st.sidebar.button(
    "🔄 Refresh",
    use_container_width=True,
):

    st.rerun()


# ============================================================
# EXISTING COMPANY VIEW
# ============================================================

if companies:

    st.markdown("---")

    st.subheader(
        "📚 Analyzed Companies"
    )

    company_names = [
        company["name"]
        for company in companies
    ]

    selected_name = st.selectbox(
        "Select Company",
        company_names,
    )

    selected_company = next(
        company
        for company in companies
        if company["name"] == selected_name
    )

    company_id = selected_company["id"]
    company = selected_company["name"]
    website = selected_company["website"]

    signals = get_signals(
        company_id
    )

    qualification = get_qualification(
        company_id
    )

    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    st.markdown("---")

    col1, col2 = st.columns(
        [3, 1]
    )

    with col1:

        st.subheader(
            f"🏢 {company}"
        )

    with col2:

        if website:

            st.link_button(
                "🌐 Website",
                website,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    if qualification:

        priority = qualification.get(
            "priority",
            "UNKNOWN"
        )

        if priority == "HIGH":

            st.error(
                "🔥 HIGH PRIORITY"
            )

        elif priority == "MEDIUM":

            st.warning(
                "🟡 MEDIUM PRIORITY"
            )

        elif priority == "LOW":

            st.success(
                "🟢 LOW PRIORITY"
            )

    # --------------------------------------------------------
    # QUALIFICATION
    # --------------------------------------------------------

    if qualification:

        st.subheader(
            "📊 Qualification"
        )

        score_fields = [
            ("ICP Fit", "icp_fit"),
            ("Opportunity", "opportunity_score"),
            ("Buying Intent", "buying_intent"),
            ("Signal Strength", "signal_strength"),
            ("Overall", "overall_score"),
        ]

        available_scores = [
            (label, key)
            for label, key in score_fields
            if key in qualification
        ]

        if available_scores:

            columns = st.columns(
                len(available_scores)
            )

            for column, (label, key) in zip(
                columns,
                available_scores
            ):

                with column:

                    value = qualification.get(
                        key
                    )

                    if value is not None:

                        st.metric(
                            label,
                            f"{value}/100"
                        )

        if qualification.get(
            "reason"
        ):

            st.info(
                qualification["reason"]
            )

    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------

    st.subheader(
        f"🚨 Detected GTM Signals ({len(signals)})"
    )

    if not signals:

        st.warning(
            "No signals detected."
        )

    else:

        for index, signal in enumerate(
            signals,
            start=1
        ):

            with st.container(
                border=True
            ):

                st.subheader(
                    f"{index}. "
                    f"{signal.get('signal_type', 'Unknown')}"
                )

                st.write(
                    f"**Event:** "
                    f"{signal.get('event', '')}"
                )

                st.write(
                    f"**Why it matters:** "
                    f"{signal.get('why_it_matters', '')}"
                )

                st.write(
                    f"**Evidence:** "
                    f"{signal.get('evidence', '')}"
                )

                st.caption(
                    f"💪 Strength: "
                    f"{signal.get('strength', 0)}/100"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "GTM Signal Intelligence • "
    "Streamlit + SQLite + Ollama/Qwen + Gmail SMTP"
)