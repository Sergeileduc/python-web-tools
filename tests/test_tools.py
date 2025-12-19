import pytest

from python_tools_sl.decorators.pauses import with_pause, with_pause_async
from python_web_tools_sl.soup_helpers import (  # noqa: F401
    aextract_form_from_url,
    amake_soup,
    extract_form,
    extract_form_from_url,
    extract_name_value_pairs,
    make_soup,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# def test_select_tag_wikipedia_ironman():
#     url = "https://fr.wikipedia.org/wiki/Iron_Man"
#     soup = make_soup(url, backend="playwright", headers=HEADERS, timeout=20)

#     tags = select_tag(soup, "meta")
#     assert "viewport" in tags
#     assert tags["viewport"].startswith("width=")
#     assert "generator" in tags
#     assert "MediaWiki" in tags["generator"]


@with_pause(2, message="ouais, pause de 2 secondes pour pas se faire timeout")
def test_extract_name_value_pairs_syc():
    LOGIN_URL = "https://secure.lemonde.fr/sfuser/connexion"
    soup = make_soup(LOGIN_URL, headers=HEADERS, timeout=20)
    form = soup.select_one('form[method="post"]')
    payload = extract_name_value_pairs(form, "input")

    assert isinstance(payload, dict)
    assert "csrf" in payload
    assert "signin" in payload
    # Les champs email/password ne sont pas dans le HTML → tu les ajoutes toi-même
    payload["email"] = "dummy@example.com"
    payload["password"] = "secret"
    assert payload["email"] == "dummy@example.com"
    assert payload["password"] == "secret"


@pytest.mark.asyncio
@with_pause_async(2, message="pause async de 2 secondes pour souffler")
async def test_extract_name_value_pairs_async():
    LOGIN_URL = "https://secure.lemonde.fr/sfuser/connexion"
    soup = await amake_soup(LOGIN_URL, headers=HEADERS, timeout=120)
    form = soup.select_one('form[method="post"]')
    payload = extract_name_value_pairs(form, "input")

    assert "csrf" in payload
    payload["email"] = "dummy@example.com"
    payload["password"] = "secret"
    assert payload["email"] == "dummy@example.com"
    assert payload["password"] == "secret"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


@with_pause(2, message="pause après chaque test backend")
@pytest.mark.parametrize("backend", ["playwright", "requests"])
def test_extract_form_from_url_with_timeout(backend):
    LOGIN_URL = "https://secure.lemonde.fr/sfuser/connexion"
    # Appel avec timeout explicite
    payload = extract_form_from_url(
        LOGIN_URL,
        headers=HEADERS,
        backend=backend,
        timeout=120,  # timeout court pour le test
    )

    # Vérifie que les champs cachés sont présents
    assert "csrf" in payload
    assert "signin" in payload

    # Ajoute les credentials simulés
    payload["email"] = "dummy@example.com"
    payload["password"] = "dummy123"

    # Vérifie que les champs utilisateurs sont bien ajoutés
    assert payload["email"] == "dummy@example.com"
    assert payload["password"] == "dummy123"


@pytest.mark.asyncio
@with_pause_async(2, message="pause async de 2 secondes pour souffler")
async def test_aextract_form_from_url_with_timeout():
    LOGIN_URL = "https://secure.lemonde.fr/sfuser/connexion"
    # Appel async avec timeout explicite
    payload = await aextract_form_from_url(
        LOGIN_URL,
        headers=HEADERS,
        backend="aiohttp",
        timeout=120,  # timeout court pour le test
    )

    # Vérifie que les champs cachés sont présents
    assert "csrf" in payload
    assert "signin" in payload

    # Ajoute les credentials simulés
    payload["email"] = "dummy@example.com"
    payload["password"] = "dummy123"

    # Vérifie que les champs utilisateurs sont bien ajoutés
    assert payload["email"] == "dummy@example.com"
    assert payload["password"] == "dummy123"
