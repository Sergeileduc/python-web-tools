"""File for some tools."""

import aiohttp
import requests
import logging
from typing import Optional  # noqa
import warnings


from requests_html import AsyncHTMLSession

from bs4 import BeautifulSoup
from discord.utils import find as disc_find

try:
    from requests_html import HTMLSession
    HAS_REQUESTS_HTML = True
except ImportError:
    HAS_REQUESTS_HTML = False


logger = logging.getLogger(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}  # noqa:E501


def make_soup(
    url: str,
    parser: str = "html.parser",
    timeout: int = 3,
    ssl: bool = True,
    backend: str = "requests",
    headers=None,
) -> BeautifulSoup:
    """
    Télécharge le contenu HTML d'une URL en mode synchrone et retourne un objet BeautifulSoup.

    Args:
        url (str): L'URL de la page à récupérer.
        parser (str, optional): Parser utilisé pour analyser le HTML.
            - "html.parser" (par défaut) : parser intégré à Python, rapide et sans dépendance externe.
            - "lxml" : nécessite l'installation de lxml, plus rapide et robuste.
            - "html5lib" : parser fidèle au standard HTML5.
        timeout (int, optional): Timeout en secondes pour la requête (par défaut 3).
        ssl (bool, optional): Active/désactive la vérification SSL (par défaut True).
            ⚠️ Avec requests, `ssl=False` équivaut à `verify=False`.
        backend (str, optional): Choix du backend HTTP.
            - "requests" (par défaut)
            - "requests_html" : exécute aussi le JavaScript (si installé).
        headers (dict, optional): En-têtes HTTP supplémentaires à inclure dans la requête.

    Returns:
        BeautifulSoup: Objet représentant l'arbre DOM de la page.

    Raises:
        requests.exceptions.RequestException: Si la requête échoue (connexion, timeout, etc.).
        requests.exceptions.HTTPError: Si le serveur retourne un code d'erreur HTTP.

    Example:
        >>> soup = make_soup("https://example.com")
        >>> print(soup.title.string)
        'Example Domain'
    """  # noqa: E501
    if backend == "requests_html" and HAS_REQUESTS_HTML:
        # HTMLSession doit être fermé explicitement → on utilise un contexte
        with HTMLSession() as session:  # type: ignore
            resp = session.get(url, timeout=timeout, verify=ssl, headers=headers)
            resp.html.render()  # type: ignore
            return BeautifulSoup(resp.html.html, features=parser)  # type: ignore
    else:
        resp = requests.get(url, timeout=timeout, verify=ssl)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, features=parser)


async def amake_soup(
    url: str,
    parser: str = "html.parser",
    timeout: int = 3,
    ssl: bool = False,
    backend: str = "aiohttp",
    headers: dict | None = None,
) -> BeautifulSoup:
    """
    Fetch an HTML page asynchronously and return a BeautifulSoup object.

    Parameters
    ----------
    url : str
        The URL of the page to fetch.
    parser : str, optional
        Parser used by BeautifulSoup.
        - "html.parser" (par défaut)
        - "lxml"
        - "html5lib"
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
    if backend == "requests_html" and HAS_REQUESTS_HTML:
        session = AsyncHTMLSession()
        resp = await session.get(url, timeout=timeout, verify=ssl, headers=headers)  # type: ignore
        await resp.html.arender()
        return BeautifulSoup(resp.html.html, features=parser)

    elif backend == "httpx":
        import httpx
        async with httpx.AsyncClient(timeout=timeout, verify=ssl, headers=headers) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, features=parser)

    else:  # aiohttp by default
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj, headers=headers) as session:
            async with session.get(url, ssl=ssl) as resp:
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
