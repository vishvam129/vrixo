"""Legal page serving for Vrixo.

Features:
    #66 Terms of Service page
    #67 Privacy Policy page
    #68 Cookie consent banner
"""

from __future__ import annotations

from pathlib import Path

LEGAL_DIR = Path(__file__).parent


def load_terms() -> str:
    """#66: Return the Terms of Service markdown content."""
    return (LEGAL_DIR / "terms.md").read_text(encoding="utf-8")


def load_privacy() -> str:
    """#67: Return the Privacy Policy markdown content."""
    return (LEGAL_DIR / "privacy.md").read_text(encoding="utf-8")


def cookie_consent_banner_html() -> str:
    """#68: HTML snippet for a cookie consent banner."""
    return """
    <div id="vrixo-cookie-banner" style="
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background: #1a1a1a;
        color: #fff;
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.2);
        z-index: 9999;
        font-size: 0.9rem;
    ">
        <div>
            🍪 Vrixo uses cookies to keep you signed in and analyse usage.
            See our <a href="/privacy" style="color: #9cf;">Privacy Policy</a>.
        </div>
        <div>
            <button onclick="acceptCookies()" style="
                background: #9cf;
                color: #000;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            ">Accept</button>
        </div>
    </div>
    <script>
        function acceptCookies() {
            localStorage.setItem('vrixo_cookie_consent', 'accepted');
            document.getElementById('vrixo-cookie-banner').style.display = 'none';
        }
        if (localStorage.getItem('vrixo_cookie_consent') === 'accepted') {
            document.getElementById('vrixo-cookie-banner').style.display = 'none';
        }
    </script>
    """


def legal_index() -> dict[str, str]:
    """Return a dict of legal document names to their paths."""
    return {
        "terms": str(LEGAL_DIR / "terms.md"),
        "privacy": str(LEGAL_DIR / "privacy.md"),
    }
