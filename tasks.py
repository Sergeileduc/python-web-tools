import contextlib
import os
import shutil
import subprocess
import sys
import webbrowser
from itertools import chain
from pathlib import Path
from platform import uname

from invoke import task  # type: ignore

"""'Makefile' equivalent for invoke tool (invoke or inv).
# Installation
`pip install invoke`
# Usage
> inv test
> inv build
etc...
# Autocompletion
For auto completion, just run:
`source <(inv --print-completion-script bash)`
or
`source <(inv --print-completion-script zsh)`
(or add it to ~/.zshrc or ~/.bashrc)
"""


# UTILS -----------------------------------------------------------------------


def get_platform():
    """Check the platform (Windos, Linux, or WSL)."""
    u = uname()
    if u.system == 'Windows':
        return 'windows'
    elif u.system == 'Linux' and 'microsoft' in u.release:
        return 'wsl'
    else:
        return 'linux'


def get_index_path():
    """Get full path for ./htmlcov/index.html file."""
    platform = get_platform()
    if platform != "wsl":
        return Path('.').resolve() / 'htmlcov' / 'index.html'
    # TODO: this part with .strip().replace() is ugly...
    process = subprocess.run(['wslpath', '-w', '.'], capture_output=True, text=True)
    pathstr = process.stdout.strip().replace('\\', '/')
    return Path(pathstr) / 'htmlcov/index.html'


# TASKS------------------------------------------------------------------------


@task
def lint(c):
    """flake8 - static check for python files"""
    c.run("flake8 .")
    c.run("pre-commit run --all-files")


@task
def mypy(c):
    """mypy"""
    print("run mypy")
    c.run("mypy")


@task
def cleantest(c):
    """Clean artifacts like *.pyc, __pycache__, .pytest_cache, etc..."""
    # Find .pyc or .pyo files and delete them
    exclude = ('venv', '.venv')
    p = Path('.')
    genpyc = (i for i in p.rglob('*.pyc') if not str(i.parent).startswith(exclude))
    genpyo = (i for i in p.rglob('*.pyo') if not str(i.parent).startswith(exclude))
    artifacts = chain(genpyc, genpyo)
    for art in artifacts:
        os.remove(art)

    # Delete caches folders
    cache1 = p.rglob('__pycache__')
    cache2 = p.rglob('.pytest_cache')
    cache3 = p.rglob('.mypy_cache')
    caches = chain(cache1, cache2, cache3)
    for cache in caches:
        shutil.rmtree(cache)

    # Delete coverage artifacts
    with contextlib.suppress(FileNotFoundError):
        os.remove('.coverage')
        shutil.rmtree('htmlcov')


@task
def cleanbuild(c):
    """Clean dist and build"""
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree('build')
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree('dist')
    eggs = Path('.').glob('*.egg-info')
    with contextlib.suppress(FileNotFoundError):
        for egg in eggs:
            shutil.rmtree(egg)


@task
def cleandoc(c):
    """Clean documentation files."""
    p = Path('.').resolve() / "docs" / "build"
    print(p)
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(p)


@task(cleantest, cleanbuild, cleandoc)
def clean(c):
    """Equivalent to both cleanbuild and cleantest..."""
    print("Cleaning")
    pass


@task
def test(c):
    """Run tests with pytest."""
    c.run("pytest tests/")


@task
def coverage(c):
    """Run unit-tests using pytest, with coverage reporting."""
    # use the browser defined in varenv $BROWSER
    # in WSL, if not set, example :  export BROWSER='/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'  # noqa: E501
    path = get_index_path()
    # c.run('coverage run --source=tests -m pytest')
    # c.run('coverage report -m')
    # c.run('coverage html')
    c.run('pytest --cov . --cov-report html')
    webbrowser.open(path.as_uri())


@task(cleandoc)
def doc(c):
    c.run("pushd docs && make html && popd")
    path = Path('.').resolve() / "docs" / "build" / "html" / "index.html"
    webbrowser.open(path.as_uri())


@task
def run(c):
    """
    Lance python_web_tools_sl/python_web_rools.py avec l'interpréteur Python courant.
    Fonctionne sur Windows, Linux et macOS.
    """
    script_path = Path("python_web_tools_sl") / "soup_helpers.py"
    c.run(f"{sys.executable} {script_path}")
