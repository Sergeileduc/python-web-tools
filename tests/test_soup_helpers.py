import pytest
from python_web_tools_sl.soup_helpers import amake_soup


@pytest.mark.asyncio
async def test_quotes_aiohttp():
    url = "http://quotes.toscrape.com/"
    soup = await amake_soup(url, backend="aiohttp", timeout=10)

    # Vérifie que la soup n'est pas vide
    assert soup is not None
    # Vérifie que le texte contient "Quotes"
    assert "Quotes" in soup.text
    # Vérifie que la longueur du texte est cohérente
    assert len(soup.text) > 1000
