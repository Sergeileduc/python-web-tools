import pytest

from python_tools_sl.decorators.pauses import with_pause_async
from python_web_tools_sl.soup_helpers import amake_soup


@pytest.mark.asyncio
@with_pause_async(2, message="pause async de 2 secondes pour souffler")
async def test_quotes_aiohttp():
    url = "http://quotes.toscrape.com/"
    soup = await amake_soup(url, backend="aiohttp", timeout=10)

    # Vérifie que la soup n'est pas vide
    assert soup is not None
    # Vérifie que le texte contient "Quotes"
    assert "Quotes" in soup.text
    # Vérifie que la longueur du texte est cohérente
    assert len(soup.text) > 1000


@pytest.mark.asyncio
@with_pause_async(2, message="pause async de 2 secondes pour souffler")
async def test_quotes_playwright():
    url = "http://quotes.toscrape.com/js/"
    soup = await amake_soup(url, backend="playwright", timeout=20)
    assert soup is not None
    assert "Quotes" in soup.text
    assert len(soup.text) > 1000


@pytest.mark.asyncio
@with_pause_async(2, message="pause async de 2 secondes pour souffler")
async def test_wikipedia_playwright():
    url = "https://fr.wikipedia.org/wiki/Iron_Man"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    soup = await amake_soup(url, backend="playwright", headers=headers, timeout=20)

    # Vérifie que la soup n'est pas vide
    assert soup is not None
    # Vérifie que le texte contient "Iron Man"
    assert "Iron Man" in soup.text
    # Vérifie que la longueur du texte est cohérente
    assert len(soup.text) > 4000
