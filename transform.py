# -*- coding: utf-8 -*-
import os
from io import BytesIO
import sys
import requests
from lxml import etree

# URL zdrojového feedu budeš zadávat jako GitHub Secret (FEED_URL)
FEED_URL = os.environ.get("FEED_URL")
OUT_PATH = "public/feed.xml"

def fetch_xml(url: str) -> bytes:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.content  # requests případně automaticky dekomprimuje

def transform(xml_bytes: bytes) -> bytes:
    # recover=True snese i méně dokonalé XML, huge_tree pro větší soubory
    parser = etree.XMLParser(remove_blank_text=False, recover=True, huge_tree=True)
    root = etree.fromstring(xml_bytes, parser=parser)

    # UPRAVA: pouze text uvnitř <category> (bez namespace)
    for el in root.xpath("//category"):
        if el.text:
            el.text = el.text.replace("|", ">")

    # Pokud budeš někdy chtít upravovat i <g:product_type>, můžeme to doplnit.

    return etree.tostring(root, encoding="UTF-8", xml_declaration=True)

def main():
    if not FEED_URL:
        print("Chybí proměnná prostředí FEED_URL (nastavíme v dalším kroku).", file=sys.stderr)
        sys.exit(1)
    xml_in = fetch_xml(FEED_URL)
    xml_out = transform(xml_in)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        f.write(xml_out)

if __name__ == "__main__":
    main()
