# scrape_all_robust.py
import time
import random
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ----- CONFIG -----
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
}

# ------------------------
# NEWS SITE 1 CONFIG
# ------------------------
NEWS1_URL = "https://quotes.toscrape.com/"  # <- EDIT: Replace with your first news site
NEWS1_SELECTOR = "div.quote span.text"       # <- EDIT: Update CSS selector for news titles
NEWS1_FILENAME = "news1.csv"

# ------------------------
# NEWS SITE 2 CONFIG
# ------------------------
NEWS2_URL = "https://quotes.toscrape.com/page/2/"  # <- EDIT: Replace with second news site
NEWS2_SELECTOR = "div.quote span.text"             # <- EDIT: Update CSS selector
NEWS2_FILENAME = "news2.csv"

# ------------------------
# E-COMMERCE SITE CONFIG
# ------------------------
ECOM_URL = "https://books.toscrape.com/catalogue/page-1.html"  # <- EDIT: First page of e-commerce site
PRODUCT_SELECTOR = "article.product_pod"                        # <- EDIT: Update CSS selector for product block
PRODUCT_TITLE_SELECTOR = "h3 a"                                 # <- EDIT: Product title/link selector
PRODUCT_PRICE_SELECTOR = "p.price_color"                        # <- EDIT: Product price selector
PRODUCT_RATING_SELECTOR = "p.star-rating"                       # <- EDIT: Product rating selector
PRODUCT_FILENAME = "products.csv"

# ----- FUNCTIONS -----
def fetch_html(url, retries=3):
    """Fetch HTML from a URL with retries on failure"""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"Attempt {attempt} failed for {url}: {e}")
            time.sleep(random.uniform(2, 4))
    print(f"Skipping {url} after {retries} failed attempts")
    return None

def scrape_news_paginated(base_url, selector, filename):
    """Scrape news with pagination and save incrementally"""
    items = []
    url = base_url
    page_num = 1

    while url:
        print(f"\nFetching news page {page_num}: {url}")
        html = fetch_html(url)
        if html is None:
            break  # skip page if failed

        soup = BeautifulSoup(html, "lxml")
        page_items = []

        for element in soup.select(selector):
            title = element.get_text(strip=True)
            link_tag = element.find_parent("a")
            link = urljoin(url, link_tag.get("href")) if link_tag else url
            page_items.append({"title": title, "link": link, "source": base_url})

        items.extend(page_items)

        # Save partial results
        df = pd.DataFrame(items)
        df.drop_duplicates(subset=["link"], inplace=True)
        df["scraped_at_utc"] = pd.Timestamp.utcnow()
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} items to {filename} so far")

        # Next page
        next_page = soup.select_one("li.next a")  # <- EDIT: Update if your site uses different next page selector
        url = urljoin(base_url, next_page["href"]) if next_page else None
        page_num += 1
        time.sleep(random.uniform(1, 3))

def scrape_products_paginated(base_url, product_selector, title_sel, price_sel, rating_sel, filename):
    """Scrape e-commerce products with pagination and partial saves"""
    items = []
    url = base_url
    page_num = 1

    while url:
        print(f"\nFetching product page {page_num}: {url}")
        html = fetch_html(url)
        if html is None:
            break

        soup = BeautifulSoup(html, "lxml")
        page_items = []

        for product in soup.select(product_selector):
            title_tag = product.select_one(title_sel)
            title = title_tag["title"] if title_tag else ""
            link = urljoin(url, title_tag["href"]) if title_tag else url
            price = product.select_one(price_sel).get_text(strip=True) if product.select_one(price_sel) else ""
            rating_tag = product.select_one(rating_sel)
            rating = rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else ""
            page_items.append({"title": title, "link": link, "price": price, "rating": rating, "source": base_url})

        items.extend(page_items)

        # Save partial results
        df = pd.DataFrame(items)
        df.drop_duplicates(subset=["link"], inplace=True)
        df["scraped_at_utc"] = pd.Timestamp.utcnow()
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} products to {filename} so far")

        # Next page
        next_page = soup.select_one("li.next a")  # <- EDIT: Update if your site uses different next page selector
        url = urljoin(base_url, next_page["href"]) if next_page else None
        page_num += 1
        time.sleep(random.uniform(1, 3))

# ----- MAIN -----
def main():
    scrape_news_paginated(NEWS1_URL, NEWS1_SELECTOR, NEWS1_FILENAME)
    scrape_news_paginated(NEWS2_URL, NEWS2_SELECTOR, NEWS2_FILENAME)
    scrape_products_paginated(ECOM_URL, PRODUCT_SELECTOR, PRODUCT_TITLE_SELECTOR,
                              PRODUCT_PRICE_SELECTOR, PRODUCT_RATING_SELECTOR, PRODUCT_FILENAME)

if __name__ == "__main__":
    main()
