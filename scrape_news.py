# scrape_all.py
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
NEWS1_URL = "https://quotes.toscrape.com/"  # <- update with first news site
NEWS1_SELECTOR = "div.quote span.text"       # <- update with correct CSS selector for titles
NEWS1_FILENAME = "news1.csv"

# ------------------------
# NEWS SITE 2 CONFIG
# ------------------------
NEWS2_URL = "https://quotes.toscrape.com/page/2/"  # <- update with second news site
NEWS2_SELECTOR = "div.quote span.text"             # <- update CSS selector
NEWS2_FILENAME = "news2.csv"

# ------------------------
# E-COMMERCE SITE CONFIG
# ------------------------
ECOM_URL = "https://books.toscrape.com/"          # <- update with e-commerce site
PRODUCT_SELECTOR = "article.product_pod"          # <- update selector for product block
PRODUCT_TITLE_SELECTOR = "h3 a"                   # <- selector for product title/link
PRODUCT_PRICE_SELECTOR = "p.price_color"          # <- selector for price
PRODUCT_RATING_SELECTOR = "p.star-rating"         # <- selector for rating
PRODUCT_FILENAME = "products.csv"

# ----- FUNCTIONS -----
def fetch_html(url):
    """Fetch HTML from a URL using headers"""
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.text

def scrape_news(url, selector, filename):
    """Scrape news titles and save to CSV"""
    print(f"Fetching {url} ...")
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")
    items = []

    for element in soup.select(selector):
        title = element.get_text(strip=True)
        # attempt to find link if available
        link_tag = element.find_parent("a")
        link = urljoin(url, link_tag.get("href")) if link_tag else url
        items.append({"title": title, "link": link, "source": url})

    df = pd.DataFrame(items)
    df.drop_duplicates(subset=["link"], inplace=True)
    df["scraped_at_utc"] = pd.Timestamp.utcnow()
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} items to {filename}\n")

def scrape_products(url, product_selector, title_sel, price_sel, rating_sel, filename):
    """Scrape products from e-commerce site"""
    print(f"Fetching {url} ...")
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")
    items = []

    for product in soup.select(product_selector):
        title_tag = product.select_one(title_sel)
        title = title_tag["title"] if title_tag else ""
        link = urljoin(url, title_tag["href"]) if title_tag else url
        price = product.select_one(price_sel).get_text(strip=True) if product.select_one(price_sel) else ""
        rating_tag = product.select_one(rating_sel)
        rating = rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else ""
        items.append({"title": title, "link": link, "price": price, "rating": rating, "source": url})

    df = pd.DataFrame(items)
    df.drop_duplicates(subset=["link"], inplace=True)
    df["scraped_at_utc"] = pd.Timestamp.utcnow()
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} products to {filename}\n")

# ----- MAIN -----
def main():
    scrape_news(NEWS1_URL, NEWS1_SELECTOR, NEWS1_FILENAME)
    time.sleep(random.uniform(1, 2))  # polite delay
    scrape_news(NEWS2_URL, NEWS2_SELECTOR, NEWS2_FILENAME)
    time.sleep(random.uniform(1, 2))
    scrape_products(ECOM_URL, PRODUCT_SELECTOR, PRODUCT_TITLE_SELECTOR,
                    PRODUCT_PRICE_SELECTOR, PRODUCT_RATING_SELECTOR, PRODUCT_FILENAME)

if __name__ == "__main__":
    main()
