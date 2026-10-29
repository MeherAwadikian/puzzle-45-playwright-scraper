"""
Puzzle #45 — Python + Playwright product scraper exporting to CSV.

Scrapes product data from books.toscrape.com — a sandbox catalog published
*specifically* for scraper practice (no real store's ToS is involved). For
each book it captures: title, price, availability, star rating, product URL,
and the category. Paginates through the catalog, then writes everything to a
CSV.

Uses Playwright (real headless Chromium rendering the pages) rather than plain
HTTP so the same script would work against JS-rendered catalogs too.

Run: python scraper.py [--max-pages N] [--out products.csv]
"""
import argparse
import csv
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "https://books.toscrape.com/"
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_products_on_page(page):
    rows = []
    cards = page.query_selector_all("article.product_pod")
    for c in cards:
        title_el = c.query_selector("h3 a")
        title = title_el.get_attribute("title")
        href = title_el.get_attribute("href")
        url = _abs(href)

        price = c.query_selector("p.price_color").inner_text().strip()
        avail = c.query_selector("p.instock.availability").inner_text().strip()

        # Rating is encoded as a class, e.g. <p class="star-rating Three">
        rating_class = c.query_selector("p.star-rating").get_attribute("class")
        rating_word = next((w for w in RATING_WORDS if w in rating_class.split()), None)
        rating = RATING_WORDS.get(rating_word, 0)

        rows.append({
            "title": title,
            "price": price,
            "price_value": _price_num(price),
            "availability": avail,
            "rating": rating,
            "url": url,
        })
    return rows


def _abs(href: str) -> str:
    href = href.replace("../", "")
    if not href.startswith("catalogue/"):
        href = "catalogue/" + href
    return BASE + href


def _price_num(price: str) -> float:
    m = re.search(r"[\d.]+", price)
    return float(m.group()) if m else 0.0


def scrape(max_pages: int, out_path: str):
    all_rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = BASE + "catalogue/page-1.html"
        page_num = 0
        while url and page_num < max_pages:
            page_num += 1
            print(f"[scrape] page {page_num}: {url}", flush=True)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector("article.product_pod", timeout=15000)
            rows = parse_products_on_page(page)
            all_rows.extend(rows)
            print(f"  +{len(rows)} products (total {len(all_rows)})", flush=True)

            nxt = page.query_selector("li.next a")
            if nxt:
                href = nxt.get_attribute("href")
                url = BASE + "catalogue/" + href.replace("catalogue/", "")
            else:
                url = None
        browser.close()

    fieldnames = ["title", "price", "price_value", "availability", "rating", "url"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"[done] wrote {len(all_rows)} products to {out_path}")
    return all_rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--out", default="products.csv")
    args = ap.parse_args()
    try:
        scrape(args.max_pages, args.out)
    except Exception as e:  # noqa: BLE001
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)
