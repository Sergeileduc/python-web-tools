"""File for some tools."""

import asyncio
import aiohttp
import requests
import logging
from typing import Optional  # noqa
import warnings


from requests_html import AsyncHTMLSession
from playwright.sync_api import sync_playwright


from bs4 import BeautifulSoup
from discord.utils import find as disc_find

try:
    from requests_html import HTMLSession
except ImportError:
    HTMLSession = None  # type: ignore


logger = logging.getLogger(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}  # noqa:E501


def make_soup(
    url: str,
    parser: str = "html.parser",
    timeout: int = 3,
    ssl: bool = True,
    backend: str = "requests",
    headers: dict | None = None,
    session=None,
) -> BeautifulSoup:
    """
    Fetch an HTML page and return a BeautifulSoup object.

    Parameters
    ----------
    url : str
        The URL of the page to fetch.
    parser : str, optional
        Parser used by BeautifulSoup. Default is "html.parser".
        lxml is faster and recommanded.
    timeout : int or float, optional
        Maximum request timeout in seconds. Default is 3.
    ssl : bool, optional
        Whether to verify SSL certificates. Default is True.
    backend : str, optional
        Backend to use. default "requests".
        - "requests" (par défaut) : HTML statique avec requests.
        - "requests_html" : HTMLSession + Pyppeteer (⚠ fragile, dépend de Chromium).
        - "playwright" : Playwright en mode synchrone (Chromium headless),
                         fiable pour exécuter du JavaScript.

    headers : dict, optional
        Additional HTTP headers to include in the request.
    session : requests.Session or HTMLSession, optional
        Existing session to reuse. If None, a new one is created internally.

    Returns
    -------
    BeautifulSoup
        Parsed HTML content of the page.
    """
    if backend == "requests_html" and HTMLSession is not None:
        if session is None:
            # crée et ferme automatiquement la session
            with HTMLSession() as s:
                resp = s.get(url, timeout=timeout, verify=ssl, headers=headers)
                resp.html.render()  # type: ignore
                return BeautifulSoup(resp.html.html, features=parser)  # type: ignore
        else:
            # utilise la session fournie, sans la fermer
            resp = session.get(url, timeout=timeout, verify=ssl, headers=headers)
            resp.html.render()
            return BeautifulSoup(resp.html.html, features=parser)

    elif backend == "playwright":
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout * 1000)
            html = page.content()
            browser.close()
            return BeautifulSoup(html, features=parser)

    else:
        if session is None:
            # requête jetable avec requests
            resp = requests.get(url, timeout=timeout, verify=ssl, headers=headers)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, features=parser)
        else:
            # utilise la session fournie
            resp = session.get(url, timeout=timeout, verify=ssl, headers=headers)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, features=parser)


async def amake_soup(
    url: str,
    parser: str = "html.parser",
    timeout: int = 3,
    ssl: bool = False,
    backend: str = "aiohttp",
    headers: dict | None = None,
    session=None,
) -> BeautifulSoup:
    """
    Fetch an HTML page asynchronously and return a BeautifulSoup object.

    Parameters
    ----------
    url : str
        The URL of the page to fetch.
    parser : str, optional
        Parser used by BeautifulSoup. Default is "html.parser".
        Options include "lxml" and "html5lib".
    timeout : int or float, optional
        Maximum request timeout in seconds. Default is 3.
    ssl : bool, optional
        Whether to verify SSL certificates. Default is False.
        ⚠️ With aiohttp, `ssl=False` disables certificate verification.
    backend : str, optional
        HTTP backend to use. Default is "aiohttp".
        - "aiohttp" : uses aiohttp.ClientSession
        - "requests_html" : uses AsyncHTMLSession (if installed)
        - "httpx" : uses httpx.AsyncClient
    headers : dict, optional
        Additional HTTP headers to include in the request.
    session : AsyncHTMLSession, aiohttp.ClientSession or httpx.AsyncClient, optional
        Existing async session to reuse. If None, a new one is created internally.

    Returns
    -------
    BeautifulSoup
        Parsed HTML content of the page.

    Raises
    ------
    aiohttp.ClientError
        If the request fails (connection, timeout, etc.).
    aiohttp.ClientResponseError
        If the server returns an HTTP error status.

    Examples
    --------
    >>> soup = await amake_soup("https://example.com")
    >>> print(soup.title.string)
    'Example Domain'
    """
    if backend == "requests_html" and AsyncHTMLSession is not None:
        if session is None:
            session = AsyncHTMLSession()
            # type: ignore
            resp = await session.get(url, timeout=timeout, verify=ssl, headers=headers)
            await resp.html.arender()
            return BeautifulSoup(resp.html.html, features=parser)
        else:
            # type: ignore
            resp = await session.get(url, timeout=timeout, verify=ssl, headers=headers)
            await resp.html.arender()
            return BeautifulSoup(resp.html.html, features=parser)

    elif backend == "httpx":
        import httpx
        if session is None:
            async with httpx.AsyncClient(timeout=timeout, verify=ssl, headers=headers) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return BeautifulSoup(resp.text, features=parser)
        else:
            resp = await session.get(url, headers=headers)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, features=parser)

    else:  # aiohttp par défaut
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        if session is None:
            async with aiohttp.ClientSession(timeout=timeout_obj, headers=headers) as client:
                async with client.get(url, ssl=ssl) as resp:
                    resp.raise_for_status()
                    text = await resp.text()
                    return BeautifulSoup(text, features=parser)
        else:
            async with session.get(url, ssl=ssl, headers=headers) as resp:
                resp.raise_for_status()
                text = await resp.text()
                return BeautifulSoup(text, features=parser)


def soup_from_text(text: str, parser: str = "html.parser") -> BeautifulSoup:
    """
    Construit un objet BeautifulSoup directement à partir d'une chaîne HTML.

    Args:
        text (str): Chaîne contenant du HTML brut.
        parser (str, optional): Parser utilisé pour analyser le HTML.
            - "html.parser" (par défaut)
            - "lxml"
            - "html5lib"

    Returns:
        BeautifulSoup: Objet représentant l'arbre DOM du HTML fourni.

    Example:
        >>> html = "<html><head><title>Hello</title></head><body>World</body></html>"
        >>> soup = soup_from_text(html)
        >>> print(soup.title.string)
        'Hello'
    """  # noqa: E501
    return BeautifulSoup(text, features=parser)


def select_tag(soup: BeautifulSoup, selector: str) -> dict:
    """Select tag in soup and return dict (name:value)."""
    items = soup.select(selector)
    return {i['name']: i['value'] for i in items if i.has_attr('name') if i.has_attr('value')}  # noqa: E501


######################################################################################
# LEGACY
######################################################################################

async def get_soup_lxml(url: str) -> BeautifulSoup:
    """Return a BeautifulSoup soup from given url, Parser is lxml.

    Args:
        url (str): url

    Returns:
        BeautifulSoup: soup

    """
    warnings.warn(
        "get_soup_lxml est obsolète, utilisez make_soup ou amake_soup",
        DeprecationWarning,
        stacklevel=2
    )

    # get HTML page with async GET request
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               timeout=aiohttp.ClientTimeout(total=3),
                               ssl=False, headers=headers) as resp:
            text = await resp.text()
    return BeautifulSoup(text, 'lxml')


async def get_soup_html(url: str) -> BeautifulSoup:
    """Return a BeautifulSoup soup from given url, Parser is html.parser.

    Args:
        url (str): url

    Returns:
        BeautifulSoup: soup

    """
    warnings.warn(
        "get_soup_html est obsolète, utilisez make_soup ou amake_soup",
        DeprecationWarning,
        stacklevel=2
    )
    # get HTML page with async GET request
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               timeout=aiohttp.ClientTimeout(total=3),
                               ssl=False) as resp:
            text = await resp.text()
    # BeautifulSoup will transform raw HTML in a tree easy to parse
    return BeautifulSoup(text, features='html.parser')


def args_separator_for_log_function(guild, args):
    """Check the args if there are user, channel and command."""
    commands = ['kick', 'clear', 'ban']
    [user, command, channel] = [None, None, None]  # They are defaulted to None, if any of them is specified, it will be changed  # noqa:E501
    for word in args:
        # if disc_get(guild.members, name=word) is not None: # if word is a member of the guild  # noqa:E501
        if disc_find(lambda m: m.name.lower() == word.lower(), guild.members) is not None:  # same, but case insensitive  # noqa:E501
            user = word.lower()
        # elif disc_get(guild.text_channels, name=word) is not None: # if word is a channel of the guild  # noqa:E501
        elif disc_find(lambda t: t.name.lower() == word.lower(), guild.text_channels) is not None:  # same, but case insensitive  # noqa:E501
            channel = word.lower()
        elif word in commands:  # if word is a command
            command = word.lower()
    # variables not specified in the args are defaulted to None
    return [user, command, channel]


async def get_soup_xml(url: str) -> BeautifulSoup:
    """Return a BeautifulSoup soup from given url, Parser is xml.

    Args:
        url (str): url

    Returns:
        BeautifulSoup: soup

    """
    warnings.warn(
        "get_soup_xml est obsolète, utilisez make_soup ou amake_soup",
        DeprecationWarning,
        stacklevel=2
    )
    asession = AsyncHTMLSession()
    r = await asession.get(url, headers=headers, timeout=3)
    await asession.close()
    return BeautifulSoup(r.text, 'xml')


if __name__ == "__main__":

    def test_make_soup_ironman():
        url = "https://fr.wikipedia.org/wiki/Iron_Man"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        print("=== Test sync make_soup (requests) ===")
        soup = make_soup(url, backend="requests", headers=headers)
        print("Titre:", soup.find("h1").text)
        print("Premier paragraphe:", soup.find("p").text)

        print("=== Test sync make_soup (playwright) ===")
        soup_pw = make_soup(url, backend="playwright", headers=headers, timeout=15000)
        print("Titre (playwright):", soup_pw.find("h1").text)
        print("Premier paragraphe (playwright):", soup_pw.find("p").text)

    def test_make_soup_airbnb():
        url = "https://www.airbnb.com/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        print("=== Test sync make_soup (requests) ===")
        soup = make_soup(url, backend="requests", headers=headers, timeout=10)
        print("Contenu brut (requests):", soup.find("div"))

        print("=== Test sync make_soup (playwright) ===")
        soup_pw = make_soup(url, backend="playwright", headers=headers, timeout=15)
        print("Contenu rendu (playwright):", soup_pw.find("div"))
    
    def test_make_soup_dynamic():
        url = "https://coinmarketcap.com/"
        print("=== requests ===")
        soup_req = make_soup(url, backend="requests", timeout=10)
        print("Longueur HTML (requests):", len(soup_req.text))

        print("=== playwright ===")
        soup_pw = make_soup(url, backend="playwright", timeout=20)
        print("Longueur HTML (playwright):", len(soup_pw.text))

    def test_make_soup_twitter():
        print("----------TEST TWITTER-------------")
        url = "https://x.com/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        print("=== requests ===")
        soup_req = make_soup(url, backend="requests", headers=headers, timeout=10)
        print("Longueur HTML (requests):", len(soup_req.text))

        print("\n=== playwright ===")
        soup_pw = make_soup(url, backend="playwright", headers=headers, timeout=20)
        print("Longueur HTML (playwright):", len(soup_pw.text))

    test_make_soup_ironman()
    test_make_soup_airbnb()
    test_make_soup_dynamic()
    test_make_soup_twitter()
