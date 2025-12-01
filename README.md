# python-web-tools-sl

Routines de scraping HTML unifiées (sync/async) avec BeautifulSoup, basées sur `requests`, `aiohttp`, `requests-html` et `httpx`.

## Installation

Depuis GitHub :

pip install git+<https://github.com/Sergeileduc/python-web-tools.git@main>

## Import

⚠️ Le package interne s’appelle **python_web_tools_sl** :

from python_web_tools_sl import make_soup, amake_soup, soup_from_text

## Usage

### Exemple synchrone

from python_web_tools_sl import make_soup

soup = make_soup("<https://example.com>")
print(soup.title.string)

### Exemple asynchrone

import asyncio
from python_web_tools_sl import amake_soup

async def main():
    soup = await amake_soup("<https://example.com>")
    print(soup.title.string)

asyncio.run(main())

### Exemple depuis du HTML brut

from python_web_tools_sl import soup_from_text

html = "<html><head><title>Hello</title></head><body>World</body></html>"
soup = soup_from_text(html)
print(soup.title.string)  # "Hello"

## Dépendances

- requests
- aiohttp
- beautifulsoup4
- lxml
- html5lib

Extras :

- requests-html
- httpx

## Notes

- Le repo GitHub s’appelle **python-web-tools** (sans suffixe).
- Le package installé et importé est **python_web_tools_sl** (avec suffixe).
