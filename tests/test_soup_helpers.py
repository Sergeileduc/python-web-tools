from time import sleep
import pytest
from python_web_tools_sl.soup_helpers import make_soup, is_dynamic, choose_backend

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


@pytest.mark.parametrize("backend", ["requests", "playwright"])
def test_make_soup_wikipedia(backend):
    url = "https://fr.wikipedia.org/wiki/Iron_Man"
    soup = make_soup(url, backend=backend, headers=HEADERS, timeout=15)
    assert soup is not None
    assert "Iron Man" in soup.text
    assert len(soup.text) > 4000
    sleep(2)


@pytest.mark.parametrize("backend", ["requests", "playwright"])
def test_make_soup_airbnb(backend):
    url = "https://www.airbnb.com/"
    soup = make_soup(url, backend=backend, headers=HEADERS, timeout=120)
    assert soup is not None
    assert soup.find("div") is not None
    sleep(2)


@pytest.mark.parametrize("backend", ["requests", "playwright"])
def test_make_soup_dynamic_coinmarketcap(backend):
    url = "https://coinmarketcap.com/"
    soup = make_soup(url, backend=backend, headers=HEADERS, timeout=50)
    assert soup is not None
    assert len(soup.text) > 1000
    sleep(2)


@pytest.mark.parametrize("backend", ["requests", "playwright"])
def test_make_soup_twitter(backend):
    url = "https://x.com/"
    soup = make_soup(url, backend=backend, headers=HEADERS, timeout=240)
    assert soup is not None
    assert len(soup.text) > 500
    sleep(2)


def test_is_dynamic_and_choose_backend():
    urls_expected = {
        "https://fr.wikipedia.org/wiki/Iron_Man": False,   # attendu: statique
        "http://quotes.toscrape.com/js/": True,            # attendu: dynamique
        "https://x.com/": True                             # attendu: dynamique
    }
    for url, expected in urls_expected.items():
        result = is_dynamic(url,
                            headers=HEADERS, threshold_ratio=1.2,
                            timeout_req=60, timeout_pw=120,
                            )
        assert result == expected

    for url in urls_expected.keys():
        backend = choose_backend(url, headers=HEADERS)
        soup = make_soup(url, backend=backend, timeout=120, headers=HEADERS)
        assert soup is not None
        assert len(soup.text) > 500
    sleep(2)
