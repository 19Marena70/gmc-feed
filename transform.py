# -*- coding: utf-8 -*-
import os
import sys
import time
import requests
from lxml import etree

# URL zdrojového feedu je v GitHub secretu FEED_URL (nastaveno už dřív)
FEED_URL = os.environ.get("FEED_URL")
OUT_PATH = "public/feed.xml"

def fetch_xml(url: str) -> bytes:
    """Stáhne XML s přátelskými hlavičkami a jednoduchým retry."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
        "Referer": "https://www.mechaneo.cz/",
    }
    last_exc = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
            r.raise_for_status()
            return r.content
        except Exception as e:
            last_exc = e
            time.sleep(2 ** attempt)  # 1s, 2s
    raise last_exc

def transform(xml_bytes: bytes) -> bytes:
    """Nahradí '|' za '>' pouze v elementu <category>."""
    parser = etree.XMLParser(remove_blank_text=False, recover=True, huge_tree=True)
    root = etree.fromstring(xml_bytes, parser=parser)

    # <category> bez namespace
    for el in root.xpath("//category"):
        if el.text:
            el.text = el.text.replace("|", ">")

    # Kdybys někdy chtěl i <g:product_type>, můžeme snadno doplnit.
    return etree.tostring(root, encoding="UTF-8", xml_declaration=True)

def main():
    if not FEED_URL:
        print("Chybí proměnná prostředí FEED_URL.", file=sys.stderr)
        sys.exit(1)
    xml_in = fetch_xml(FEED_URL)
    xml_out = transform(xml_in)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        f.write(xml_out)

if __name__ == "__main__":
    main()
