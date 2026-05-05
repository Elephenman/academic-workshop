#!/usr/bin/env python3
"""
win_compat.py - Windows Compatibility Shim for Academic Workshop

Solves two systemic issues on Windows:
  - RED-01: Chinese chars in sys.path cause C-extension DLL load failures
  - RED-03: Console GBK encoding cannot handle emoji/unicode in print()

Usage (at the TOP of every entry-point script, before other imports):
    import win_compat  # noqa: F401  -- must be first import

Or import and call explicitly:
    from win_compat import fix_path, fix_encoding
    fix_path()
    fix_encoding()
"""

import sys
import os


def fix_path() -> None:
    """RED-01: Ensure site-packages is on sys.path even when the Python
    prefix contains non-ASCII characters (e.g. Chinese usernames).

    Python C extensions (PyMuPDF/fitz, lxml, etc.) use ctypes.LoadLibrary
    which fails on non-ASCII paths on Windows.  Adding the resolved
    site-packages directory works around this in most cases.
    """
    if sys.platform != 'win32':
        return

    site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
    site_packages = os.path.normpath(site_packages)

    if site_packages not in sys.path:
        sys.path.insert(0, site_packages)

    # Also try the user-level site-packages
    try:
        import site
        user_site = site.getusersitepackages()
        if user_site and user_site not in sys.path:
            sys.path.insert(0, user_site)
    except Exception:
        pass


def fix_encoding() -> None:
    """RED-03: Reconfigure stdout/stderr to UTF-8 on Windows.

    Windows console defaults to GBK (cp936) which cannot encode emoji
    or many CJK extension characters, causing UnicodeEncodeError on
    print() calls.
    """
    if sys.platform != 'win32':
        return

    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass


# Auto-fix on import
fix_path()
fix_encoding()
