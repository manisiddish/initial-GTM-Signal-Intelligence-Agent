import re


# ============================================================
# GARBAGE / WEBSITE NOISE
# ============================================================

GARBAGE_PHRASES = [
    "this is some text inside of a div block",
    "log in to claude",
    "download app",
    "menu",
    "navigation",
    "cookie",
    "sign in",
    "login",
]


# ============================================================
# ALLOWED SIGNAL TYPES
# ============================================================

ALLOWED_TYPES = {
    "product_launch",
    "hiring",
    "funding",
    "market_expansion",
    "partnership",
    "leadership_change",
    "technology_change",
    "pricing_change",
    "sales_expansion",
    "marketing_expansion",
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    text = str(text or "").lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# GET SIGNAL TYPE
# ============================================================

def get_signal_type(signal: dict) -> str:
    signal_type = signal.get("signal_type")

    if not signal_type:
        signal_type = signal.get("type")

    return str(
        signal_type or ""
    ).strip().lower()


# ============================================================
# CHECK EXPLICIT BUSINESS EVENT
# ============================================================

def is_explicit_business_event(signal: dict) -> bool:

    signal_type = get_signal_type(signal)

    event = str(
        signal.get("event", "")
    ).strip().lower()

    evidence = str(
        signal.get("evidence", "")
    ).strip().lower()

    if not event or not evidence:
        return False


    # --------------------------------------------------------
    # PRODUCT LAUNCH
    # --------------------------------------------------------

    if signal_type == "product_launch":

        launch_words = [
            # English
            "launched",
            "launch",
            "released",
            "release",
            "introduced",
            "introducing",
            "announced",
            "announces",
            "unveiled",
            "now available",
            "new product",
            "new model",
            "new platform",
            "new service",

            # German
            "eingeführt",
            "einführung",
            "vorgestellt",
            "veröffentlicht",
            "veröffentlichung",
            "angekündigt",
            "ankündigung",
            "jetzt verfügbar",
            "neu verfügbar",
            "neues produkt",
            "neues modell",
            "neue plattform",
            "neuer service",
        ]

        return any(
            word in evidence
            for word in launch_words
        )


    # --------------------------------------------------------
    # MARKET EXPANSION
    # --------------------------------------------------------

    if signal_type == "market_expansion":

        expansion_words = [
            "expanded into",
            "expanding into",
            "entered the market",
            "entering the market",
            "launched in",
            "expansion into",
            "expanded to",
            "expanding to",
            "entered",
            "new market",
            "international expansion",
            "global expansion",

            # German
            "expandiert",
            "expansion",
            "ausgeweitet",
            "erweitert",
            "neuen markt",
            "markt erweitert",
            "in den markt",
            "international expandiert",
            "international expansion",
        ]

        return any(
            word in evidence
            for word in expansion_words
        )


    # --------------------------------------------------------
    # HIRING
    # --------------------------------------------------------

    if signal_type == "hiring":

        hiring_words = [
            "hiring",
            "recruiting",
            "headcount increased",
            "workforce growth",
            "hiring plans",
            "expanding the team",
            "hired",
            "new employees",
            "new roles",
            "open positions",
            "job openings",
            "recruitment",

            # German
            "einstellung",
            "einstellungen",
            "stellt ein",
            "stellenangebote",
            "personalaufbau",
            "team erweitert",
            "teamaufbau",
            "neue mitarbeiter",
            "offene stellen",
            "stellen",
        ]

        return any(
            word in evidence
            for word in hiring_words
        )


    # --------------------------------------------------------
    # FUNDING
    # --------------------------------------------------------

    if signal_type == "funding":

        funding_words = [
            "raised",
            "funding round",
            "funding",
            "investment",
            "invested",
            "fundraise",
            "fundraising",
            "series a",
            "series b",
            "series c",
            "series d",
            "venture capital",
            "capital raised",

            # German
            "finanzierung",
            "finanzierungsrunde",
            "investition",
            "investiert",
            "kapital aufgenommen",
            "kapitalrunde",
            "finanzierungsrunde",
        ]

        return any(
            word in evidence
            for word in funding_words
        )


    # --------------------------------------------------------
    # PARTNERSHIP
    # --------------------------------------------------------

    if signal_type == "partnership":

        partnership_words = [
            "partnered with",
            "partnership with",
            "strategic partnership",
            "announced a partnership",
            "collaboration with",
            "partnered",
            "strategic collaboration",
            "joined forces",

            # German
            "partnerschaft",
            "partnerschaft mit",
            "strategische partnerschaft",
            "zusammenarbeit mit",
            "kooperation mit",
            "partnerschaft angekündigt",
        ]

        return any(
            word in evidence
            for word in partnership_words
        )


    # --------------------------------------------------------
    # LEADERSHIP CHANGE
    # --------------------------------------------------------

    if signal_type == "leadership_change":

        leadership_words = [
            "appointed",
            "promoted",
            "joined as ceo",
            "joined as cto",
            "joined as cfo",
            "new ceo",
            "new cto",
            "new cfo",
            "leadership change",
            "new chief",
            "appointed as",
            "named as",

            # German
            "ernannt",
            "befördert",
            "neuer ceo",
            "neuer cto",
            "neuer cfo",
            "geschäftsführer",
            "vorstand",
            "führungsteam",
            "neuer chef",
        ]

        return any(
            word in evidence
            for word in leadership_words
        )


    # --------------------------------------------------------
    # PRICING CHANGE
    # --------------------------------------------------------

    if signal_type == "pricing_change":

        pricing_words = [
            "price increase",
            "price decrease",
            "pricing changed",
            "pricing change",
            "new pricing",
            "reduced price",
            "increased price",
            "prices increased",
            "prices decreased",
            "new pricing model",
            "pricing model",

            # German
            "preiserhöhung",
            "preissenkung",
            "preisänderung",
            "neue preise",
            "neue preismodelle",
            "preise erhöht",
            "preise gesenkt",
            "preis geändert",
        ]

        return any(
            word in evidence
            for word in pricing_words
        )


    # --------------------------------------------------------
    # TECHNOLOGY CHANGE
    # --------------------------------------------------------

    if signal_type == "technology_change":

        technology_words = [
            "introduced new technology",
            "announced new technology",
            "technology upgrade",
            "technology migration",
            "migrated to",
            "adopted",
            "deployed",
            "implemented",
            "new technology",
            "technology platform",
            "technical upgrade",
            "infrastructure upgrade",

            # German
            "neue technologie",
            "technologie eingeführt",
            "technologie vorgestellt",
            "technologie upgrade",
            "technologie aktualisiert",
            "technologie migration",
            "migriert",
            "eingesetzt",
            "implementiert",
            "technologieplattform",
        ]

        return any(
            word in evidence
            for word in technology_words
        )


    # --------------------------------------------------------
    # SALES EXPANSION
    # --------------------------------------------------------

    if signal_type == "sales_expansion":

        sales_words = [
            "expanded sales",
            "sales expansion",
            "expanded sales team",
            "sales team growth",
            "new sales team",
            "sales hiring",
            "sales organization",
            "sales growth",

            # German
            "vertrieb erweitert",
            "vertriebsausbau",
            "vertriebsteam erweitert",
            "neues vertriebsteam",
            "vertriebsteam wächst",
            "vertrieb eingestellt",
            "vertriebsausbau",
        ]

        return any(
            word in evidence
            for word in sales_words
        )


    # --------------------------------------------------------
    # MARKETING EXPANSION
    # --------------------------------------------------------

    if signal_type == "marketing_expansion":

        marketing_words = [
            "expanded marketing",
            "marketing expansion",
            "marketing team growth",
            "new marketing campaign",
            "marketing initiative",
            "marketing hiring",
            "new campaign",
            "marketing expansion",

            # German
            "marketing erweitert",
            "marketingausbau",
            "marketingteam erweitert",
            "neue marketingkampagne",
            "marketinginitiative",
            "marketing eingestellt",
        ]

        return any(
            word in evidence
            for word in marketing_words
        )


    return False


# ============================================================
# BROADER BUSINESS ACTION CHECK
# ============================================================

def has_business_action(signal: dict) -> bool:

    event = str(
        signal.get("event", "")
    ).strip().lower()

    evidence = str(
        signal.get("evidence", "")
    ).strip().lower()

    combined = f"{event} {evidence}"

    business_action_words = [

        # Product / launch
        "launched",
        "launch",
        "released",
        "release",
        "introduced",
        "announced",
        "unveiled",
        "new product",
        "new platform",
        "new service",

        # Growth
        "expanded",
        "expansion",
        "entered",
        "new market",
        "international expansion",
        "global expansion",

        # Hiring
        "hiring",
        "hired",
        "recruiting",
        "recruitment",
        "new employees",
        "new roles",
        "job openings",

        # Funding
        "raised",
        "funding",
        "investment",
        "invested",
        "fundraising",
        "funding round",
        "series a",
        "series b",
        "series c",

        # Partnership
        "partnership",
        "partnered",
        "collaboration",
        "strategic partnership",
        "joined forces",

        # Leadership
        "appointed",
        "promoted",
        "new ceo",
        "new cto",
        "new cfo",
        "leadership change",

        # Pricing
        "pricing change",
        "pricing changed",
        "new pricing",
        "price increase",
        "price decrease",
        "pricing model",
        "prices increased",
        "prices decreased",

        # Technology
        "new technology",
        "technology upgrade",
        "technology migration",
        "migrated to",
        "adopted",
        "deployed",
        "implemented",
        "technical upgrade",

        # Sales
        "sales expansion",
        "expanded sales",
        "sales team growth",
        "new sales team",
        "sales hiring",

        # Marketing
        "marketing expansion",
        "expanded marketing",
        "marketing team growth",
        "new marketing campaign",
        "marketing initiative",

        # German
        "eingeführt",
        "einführung",
        "vorgestellt",
        "veröffentlicht",
        "angekündigt",
        "expandiert",
        "ausgeweitet",
        "erweitert",
        "neuen markt",
        "einstellung",
        "einstellungen",
        "stellenangebote",
        "personalaufbau",
        "finanzierung",
        "finanzierungsrunde",
        "investition",
        "partnerschaft",
        "kooperation",
        "ernannt",
        "befördert",
        "neuer ceo",
        "neuer cto",
        "neuer cfo",
        "preiserhöhung",
        "preissenkung",
        "preisänderung",
        "neue preise",
        "neue technologie",
        "implementiert",
        "vertriebsausbau",
        "marketingausbau",
    ]

    return any(
        word in combined
        for word in business_action_words
    )


# ============================================================
# VALIDATE SIGNAL
# ============================================================

def is_valid_signal(signal: dict) -> bool:

    if not isinstance(signal, dict):
        return False

    event = str(
        signal.get("event", "")
    ).strip()

    evidence = str(
        signal.get("evidence", "")
    ).strip()

    signal_type = get_signal_type(signal)


    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    if not event or not evidence:
        return False


    # --------------------------------------------------------
    # Allowed signal type
    # --------------------------------------------------------

    if signal_type not in ALLOWED_TYPES:
        return False


    # --------------------------------------------------------
    # Evidence length
    # --------------------------------------------------------

    if len(evidence) < 15:
        return False


    # --------------------------------------------------------
    # Website garbage
    # --------------------------------------------------------

    combined = (
        event + " " + evidence
    ).lower()

    for phrase in GARBAGE_PHRASES:

        if phrase in combined:
            return False


    # --------------------------------------------------------
    # Static website listings
    # --------------------------------------------------------

    static_listing_phrases = [
        "products ...",
        "products:",
        "solutions:",
        "models ...",
        "models:",
    ]

    if any(
        phrase in evidence.lower()
        for phrase in static_listing_phrases
    ):

        if not is_explicit_business_event(signal):

            # Static website content is normally not a signal.
            # Only keep it if there is another strong business
            # action in the evidence.
            if not has_business_action(signal):
                return False


    # --------------------------------------------------------
    # Final evidence validation
    # --------------------------------------------------------

    if not is_explicit_business_event(signal):

        # The old validator was too strict and rejected valid
        # business events simply because Qwen used different wording.
        #
        # We now allow longer evidence when it clearly contains
        # a business action.

        if len(evidence) < 40:
            return False

        if not has_business_action(signal):
            return False


    return True


# ============================================================
# EXTRACT PRODUCT NAMES
# ============================================================

def get_product_names(signal: dict) -> set:

    text = " ".join(
        [
            str(signal.get("event", "")),
            str(signal.get("evidence", "")),
        ]
    ).lower()

    products = set()

    known_products = [
        "sonnet 5.5",
        "opus 5.5",
        "fable 5.1",
        "mythos 5.1",
    ]

    for product in known_products:

        if product in text:
            products.add(product)

    return products


# ============================================================
# DEDUPLICATE SIGNALS
# ============================================================

def deduplicate_signals(signals: list) -> list:

    unique = []

    seen_events = set()
    seen_products = set()

    for signal in signals:

        event = str(
            signal.get("event", "")
        )

        normalized_event = normalize_text(
            event
        )

        if not normalized_event:
            continue


        # ----------------------------------------------------
        # Exact event duplicate
        # ----------------------------------------------------

        if normalized_event in seen_events:
            continue


        # ----------------------------------------------------
        # Product-level duplicate
        # ----------------------------------------------------

        products = get_product_names(
            signal
        )

        duplicate_product = False

        for product in products:

            if product in seen_products:

                duplicate_product = True
                break

        if duplicate_product:
            continue


        # ----------------------------------------------------
        # Keep signal
        # ----------------------------------------------------

        unique.append(signal)

        seen_events.add(
            normalized_event
        )

        seen_products.update(
            products
        )


    return unique


# ============================================================
# MAIN SIGNAL CLEANER
# ============================================================

def clean_signals(signals: list) -> list:

    if not isinstance(signals, list):
        return []


    normalized_signals = []


    # --------------------------------------------------------
    # Normalize Qwen output
    # --------------------------------------------------------

    for signal in signals:

        if not isinstance(signal, dict):
            continue

        signal = dict(signal)


        # Qwen normally returns "type".
        # Database uses "signal_type".

        if not signal.get("signal_type"):

            signal["signal_type"] = signal.get(
                "type",
                ""
            )


        # Keep both fields for compatibility

        signal["type"] = signal.get(
            "signal_type",
            signal.get("type", "")
        )


        # Normalize strength

        try:

            signal["strength"] = int(
                signal.get("strength", 0)
            )

        except (
            ValueError,
            TypeError
        ):

            signal["strength"] = 0


        # Keep only reasonable strength values

        if signal["strength"] < 0:
            signal["strength"] = 0

        if signal["strength"] > 100:
            signal["strength"] = 100


        normalized_signals.append(
            signal
        )


    # --------------------------------------------------------
    # Validate signals
    # --------------------------------------------------------

    valid = [
        signal
        for signal in normalized_signals
        if is_valid_signal(signal)
    ]


    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    valid = deduplicate_signals(
        valid
    )


    # --------------------------------------------------------
    # Strongest signals first
    # --------------------------------------------------------

    valid.sort(
        key=lambda x: x.get(
            "strength",
            0
        ),
        reverse=True
    )


    # --------------------------------------------------------
    # Maximum 5 signals
    # --------------------------------------------------------

    return valid[:5]