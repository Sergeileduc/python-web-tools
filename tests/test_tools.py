import asyncio
import time

import pytest
from python_web_tools_sl.soup_helpers import (make_soup, amake_soup,
                                              extract_name_value_pairs,
                                              extract_form,
                                              extract_form_from_url,
                                              aextract_form_from_url,
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
    time.sleep(2)


@pytest.mark.asyncio
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

    await asyncio.sleep(2)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


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

    time.sleep(2)


@pytest.mark.asyncio
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

    await asyncio.sleep(2)
