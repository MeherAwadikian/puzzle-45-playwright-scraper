# Puzzle #45 — Python + Playwright product scraper → CSV

Brief (Task Forge puzzle tracker): Python + Playwright product scraper exporting to CSV — Python + Playwright.

A Playwright (headless Chromium) scraper that walks a product catalog, extracts
structured fields per product, and writes a CSV.

## Ethical target

It scrapes **books.toscrape.com** — a catalog published *specifically* as a
scraping sandbox (by the Scrapy/Zyte team). No real store's Terms of Service
are involved, which is the responsible way to demo a scraper. Point the `BASE`
constant at a different catalog to reuse the logic.

## What it extracts

Per product: `title`, `price` (raw), `price_value` (parsed float),
`availability`, `rating` (1–5, decoded from the CSS star-rating class), and the
absolute product `url`. It paginates via the catalog's "next" link up to
`--max-pages`.

Why Playwright (not plain `requests`): the script renders each page in real
headless Chromium, so the exact same code works against JS-rendered catalogs —
which plain HTTP scraping can't handle.

## Run

```
pip install playwright
python -m playwright install chromium   # one-time (downloads the browser)
python scraper.py --max-pages 5 --out products.csv
```

## Verified

Scraped the live sandbox end to end — `products.csv` (100 products, 5 pages).
Data-quality checks on the output: 100/100 rows have a title, 100/100 URLs are
valid `https://` links, 100/100 prices parsed to a float, and the star ratings
decoded to a realistic 1–5 spread (22/19/22/18/19). Sample row:
`A Light in the Attic, £51.77, 51.77, In stock, 3, <url>`.

Note (this machine only): `PLAYWRIGHT_BROWSERS_PATH` was pointed at a `D:\`
cache that intermittently disconnects, which made `playwright install` fail
with `mkdir '\\?'`. Fixed by pointing it at a `C:\` path
(`PLAYWRIGHT_BROWSERS_PATH=C:\Users\h\.ms-playwright`) before install and run.
