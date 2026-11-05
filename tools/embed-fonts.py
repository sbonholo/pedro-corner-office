#!/usr/bin/env python3
"""Rebuild the self-hosted @font-face block in index.html.

The woff2 files in fonts/ (latin subset, @fontsource 5.3.0, SIL OFL 1.1) are
embedded as data: URIs so index.html stays a single file that works offline,
from file://, and with no third-party requests.

Usage: python3 tools/embed-fonts.py
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
UR = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,"
      "U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
FACES = [  # family, weight, file, variable
    ("Bricolage Grotesque", "200 800", "bricolage-grotesque-latin-opsz-normal.woff2", True),
    ("IBM Plex Sans", "100 700", "ibm-plex-sans-latin-wght-normal.woff2", True),
    ("IBM Plex Mono", "400", "ibm-plex-mono-latin-400-normal.woff2", False),
    ("IBM Plex Mono", "500", "ibm-plex-mono-latin-500-normal.woff2", False),
]
START, END = "<style id=\"fonts\">", "</style>"


def block():
    rules = []
    for fam, wt, fn, var in FACES:
        uri = "data:font/woff2;base64," + base64.b64encode((ROOT / "fonts" / fn).read_bytes()).decode()
        src = f"url({uri}) format('woff2')"
        rules.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-display:swap;"
                     f"font-weight:{wt};src:{src};unicode-range:{UR}}}")
    return (START + "\n/* Self-hosted fonts: fonts/*.woff2 (latin subset, @fontsource 5.3.0, SIL OFL 1.1),"
            " embedded by tools/embed-fonts.py. System fallbacks in --f-* apply if they fail. */\n"
            + "\n".join(rules) + "\n" + END)


def main():
    s = HTML.read_text(encoding="utf-8")
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pat.search(s):
        raise SystemExit("font block not found in index.html")
    HTML.write_text(pat.sub(lambda _: block(), s, count=1), encoding="utf-8")
    print("index.html:", HTML.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
