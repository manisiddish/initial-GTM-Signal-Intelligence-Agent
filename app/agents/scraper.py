import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    re.IGNORECASE,
)


def normalize_url(url: str) -> str:

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def extract_emails(text: str):

    emails = EMAIL_REGEX.findall(text)

    cleaned = []

    for email in emails:

        email = email.lower().strip()

        if email not in cleaned:
            cleaned.append(email)

    return cleaned


def choose_best_email(emails):

    if not emails:
        return None

    # Prefer business/contact addresses
    preferred_words = [
        "sales",
        "contact",
        "info",
        "hello",
        "business",
        "partnership",
        "partnerships",
        "marketing",
        "growth",
        "support",
    ]

    for keyword in preferred_words:

        for email in emails:

            if email.startswith(keyword + "@"):
                return email

    # Otherwise return first public business email
    return emails[0]


def scrape_website(url: str) -> dict:

    url = normalize_url(url)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # ----------------------------------------------------
        # MAIN PAGE
        # ----------------------------------------------------

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else ""
        )

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        text = " ".join(
            text.split()
        )

        main_emails = extract_emails(
            response.text + " " + text
        )

        # ----------------------------------------------------
        # FIND CONTACT-RELATED LINKS
        # ----------------------------------------------------

        contact_links = []

        for link in soup.find_all("a", href=True):

            href = link.get("href", "")

            link_text = link.get_text(
                " ",
                strip=True
            ).lower()

            combined = (
                href.lower()
                + " "
                + link_text
            )

            if any(
                word in combined
                for word in [
                    "contact",
                    "about",
                    "team",
                    "sales",
                    "support",
                    "partnership",
                ]
            ):

                full_url = urljoin(
                    url,
                    href
                )

                parsed = urlparse(full_url)

                base_domain = urlparse(url).netloc

                if parsed.netloc == base_domain:

                    if full_url not in contact_links:

                        contact_links.append(
                            full_url
                        )

        # ----------------------------------------------------
        # SCRAPE CONTACT PAGES
        # ----------------------------------------------------

        discovered_emails = list(
            main_emails
        )

        for contact_url in contact_links[:5]:

            try:

                contact_response = requests.get(
                    contact_url,
                    headers=headers,
                    timeout=10,
                )

                if contact_response.ok:

                    page_emails = extract_emails(
                        contact_response.text
                    )

                    for email in page_emails:

                        if email not in discovered_emails:

                            discovered_emails.append(
                                email
                            )

            except requests.RequestException:

                continue

        # ----------------------------------------------------
        # SELECT BEST EMAIL
        # ----------------------------------------------------

        best_email = choose_best_email(
            discovered_emails
        )

        # ----------------------------------------------------
        # LIMIT TEXT
        # ----------------------------------------------------

        text = text[:15000]

        return {
            "success": True,
            "url": url,
            "title": title,
            "text": text,
            "emails": discovered_emails,
            "email": best_email,
            "email_source": (
                "public website"
                if best_email
                else None
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "url": url,
            "error": str(e),
            "emails": [],
            "email": None,
        }