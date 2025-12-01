"""File for some tools."""

import aiohttp
import requests
import logging
from typing import Optional

import backoff
import discord
from discord.ext import commands
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
    backend: str = "requests"
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

    Returns:
        BeautifulSoup: Objet représentant l'arbre DOM de la page.

    Raises:
        requests.exceptions.RequestException: Si la requête échoue (connexion, timeout, etc.).
        requests.exceptions.HTTPError: Si le serveur retourne un code d'erreur HTTP.

    Example:
        >>> soup = make_soup("https://example.com")
        >>> print(soup.title.string)
        'Example Domain'
    """
    if backend == "requests_html" and HAS_REQUESTS_HTML:
        session = HTMLSession()
        resp = session.get(url, timeout=timeout, verify=ssl)
        resp.html.render()
        return BeautifulSoup(resp.html.html, features=parser)
    else:
        resp = requests.get(url, timeout=timeout, verify=ssl)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, features=parser)


async def amake_soup(
    url: str,
    parser: str = "html.parser",
    timeout: int = 3,
    ssl: bool = False,
    backend: str = "aiohttp"
) -> BeautifulSoup:
    """
    Télécharge le contenu HTML d'une URL en mode asynchrone et retourne un objet BeautifulSoup.

    Args:
        url (str): L'URL de la page à récupérer.
        parser (str, optional): Parser utilisé pour analyser le HTML.
            - "html.parser" (par défaut)
            - "lxml"
            - "html5lib"
        timeout (int, optional): Timeout en secondes pour la requête (par défaut 3).
        ssl (bool, optional): Active/désactive la vérification SSL (par défaut False).
            ⚠️ Avec aiohttp, `ssl=False` désactive la vérification des certificats.
        backend (str, optional): Choix du backend HTTP.
            - "aiohttp" (par défaut)
            - "requests_html" : utilise AsyncHTMLSession (si installé).
            - "httpx" : possible extension future.

    Returns:
        BeautifulSoup: Objet représentant l'arbre DOM de la page.

    Raises:
        aiohttp.ClientError: Si la requête échoue (connexion, timeout, etc.).
        aiohttp.ClientResponseError: Si le serveur retourne un code d'erreur HTTP.

    Example:
        >>> soup = await amake_soup("https://example.com")
        >>> print(soup.title.string)
        'Example Domain'
    """
    if backend == "requests_html" and HAS_REQUESTS_HTML:
        session = AsyncHTMLSession()
        resp = await session.get(url, timeout=timeout, verify=ssl)
        await resp.html.arender()
        return BeautifulSoup(resp.html.html, features=parser)

    elif backend == "httpx":
        import httpx
        async with httpx.AsyncClient(timeout=timeout, verify=ssl) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, features=parser)

    else:  # aiohttp par défaut
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
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
    """
    return BeautifulSoup(text, features=parser)
