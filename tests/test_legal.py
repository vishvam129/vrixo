"""Tests for web.legal.pages."""

from web.legal.pages import (
    cookie_consent_banner_html,
    legal_index,
    load_privacy,
    load_terms,
)


def test_load_terms_has_content_policy() -> None:
    """#66: Terms of Service page includes content policy."""
    content = load_terms()
    assert "Terms of Service" in content
    assert "Content Policy" in content
    assert "CSAM" in content  # safety content


def test_load_terms_covers_required_sections() -> None:
    content = load_terms()
    for section in ["Acceptance", "Content Policy", "Termination", "Contact"]:
        assert section in content


def test_load_privacy_lists_data_collection() -> None:
    """#67: Privacy Policy lists what data is collected."""
    content = load_privacy()
    assert "Privacy Policy" in content
    assert "What We Collect" in content
    assert "Retention" in content


def test_load_privacy_covers_gdpr_and_dpdp() -> None:
    content = load_privacy()
    assert "GDPR" in content
    assert "DPDP" in content


def test_cookie_banner_has_accept_button() -> None:
    """#68: cookie consent banner has an accept action."""
    html = cookie_consent_banner_html()
    assert "Accept" in html
    assert "vrixo-cookie-banner" in html
    assert "localStorage" in html  # consent persistence


def test_legal_index_returns_both_docs() -> None:
    index = legal_index()
    assert "terms" in index
    assert "privacy" in index
