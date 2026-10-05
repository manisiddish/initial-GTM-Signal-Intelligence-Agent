import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

# Project root:
# Demo/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Database folder:
# Demo/data/
DATA_DIR = PROJECT_ROOT / "data"

# Database file:
# Demo/data/gtm_signals.db
DB_PATH = DATA_DIR / "gtm_signals.db"

# Make sure the data folder exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(str(DB_PATH))


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            signal_type TEXT NOT NULL,
            event TEXT NOT NULL,
            why_it_matters TEXT,
            evidence TEXT,
            strength INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (company_id)
            REFERENCES companies(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qualifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            icp_fit INTEGER DEFAULT 0,
            opportunity_score INTEGER DEFAULT 0,
            buying_intent INTEGER DEFAULT 0,
            signal_strength INTEGER DEFAULT 0,
            overall_score INTEGER DEFAULT 0,
            priority TEXT,
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (company_id)
            REFERENCES companies(id)
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# SAVE / GET COMPANY
# ============================================================

def save_company(name: str, website: str) -> int:

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT OR IGNORE INTO companies
        (name, website, created_at)
        VALUES (?, ?, ?)
        """,
        (name, website, created_at)
    )

    connection.commit()

    cursor.execute(
        """
        SELECT id
        FROM companies
        WHERE website = ?
        """,
        (website,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise RuntimeError("Could not save company.")

    return row[0]


# ============================================================
# SAVE SIGNALS
# ============================================================

def save_signals(company_id: int, signals: list):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    # --------------------------------------------------------
    # IMPORTANT:
    # Remove the company's previous signals first.
    #
    # This prevents duplicates when the same company
    # is analyzed again.
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM signals
        WHERE company_id = ?
        """,
        (company_id,)
    )

    # --------------------------------------------------------
    # Insert the fresh signals
    # --------------------------------------------------------

    for signal in signals:

        signal_type = signal.get(
            "signal_type",
            signal.get("type", "")
        )

        cursor.execute(
            """
            INSERT INTO signals
            (
                company_id,
                signal_type,
                event,
                why_it_matters,
                evidence,
                strength,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_id,
                signal_type,
                signal.get("event", ""),
                signal.get("why_it_matters", ""),
                signal.get("evidence", ""),
                signal.get("strength", 0),
                created_at
            )
        )

    connection.commit()
    connection.close()


# ============================================================
# SAVE QUALIFICATION
# ============================================================

def save_qualification(company_id: int, qualification: dict):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    # --------------------------------------------------------
    # Remove previous qualification for this company
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM qualifications
        WHERE company_id = ?
        """,
        (company_id,)
    )

    # --------------------------------------------------------
    # Save the latest qualification
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO qualifications
        (
            company_id,
            icp_fit,
            opportunity_score,
            buying_intent,
            signal_strength,
            overall_score,
            priority,
            reason,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            qualification.get("icp_fit", 0),
            qualification.get("opportunity_score", 0),
            qualification.get("buying_intent", 0),
            qualification.get("signal_strength", 0),
            qualification.get("overall_score", 0),
            qualification.get("priority", "LOW"),
            qualification.get("reason", ""),
            created_at
        )
    )

    connection.commit()
    connection.close()