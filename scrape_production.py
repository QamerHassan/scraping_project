# scrape_production.py
import time
import random
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ----- HEADERS -----
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
}

# ----- NEWS SITES CONFIG -----
NEWS_SITES = [
    {
        "url": "https://quotes.toscrape.com/",
        "selector": "div.quote span.text",
        "filename": "news1.csv"
    },
    {
        "url": "https://quotes.toscrape.com/page/2/",
        "selector": "div.quote span.text",
        "filename": "news2.csv"
    }
]

# ----- E-COMMERCE SITES CONFIG -----
ECOM_SITES = [
    {
        "url": "https://books.toscrape.com/catalogue/page-1.html",
        "product_selector": "article.product_pod",
        "title_selector": "h3 a",
        "price_selector": "p.price_color",
        "rating_selector": "p.star-rating",
        "filename": "products.csv"
    }
]

# ----- FUNCTIONS -----
def fetch_html(url, retries=3):
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

def scrape_news_site(site):
    url = site["url"]
    selector = site["selector"]
    filename = site["filename"]
    items = []
    page_num = 1

    while url:
        print(f"\nFetching news page {page_num}: {url}")
        html = fetch_html(url)
        if html is None:
            break

        soup = BeautifulSoup(html, "lxml")
        page_items = []

        for element in soup.select(selector):
            title = element.get_text(strip=True)
            link_tag = element.find_parent("a")
            link = urljoin(url, link_tag.get("href")) if link_tag else url
            page_items.append({"title": title, "link": link, "source": site["url"]})

        items.extend(page_items)

        # Save partial CSV
        df = pd.DataFrame(items)
        df.drop_duplicates(subset=["link"], inplace=True)
        df["scraped_at_utc"] = pd.Timestamp.utcnow()
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} items to {filename} so far")

        # Next page
        next_page = soup.select_one("li.next a")
        url = urljoin(site["url"], next_page["href"]) if next_page else None
        page_num += 1
        time.sleep(random.uniform(1, 3))

def scrape_ecom_site(site):
    url = site["url"]
    product_selector = site["product_selector"]
    title_sel = site["title_selector"]
    price_sel = site["price_selector"]
    rating_sel = site["rating_selector"]
    filename = site["filename"]
    items = []
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
            page_items.append({"title": title, "link": link, "price": price, "rating": rating, "source": site["url"]})

        items.extend(page_items)

        # Save partial CSV
        df = pd.DataFrame(items)
        df.drop_duplicates(subset=["link"], inplace=True)
        df["scraped_at_utc"] = pd.Timestamp.utcnow()
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} products to {filename} so far")

        # Next page
        next_page = soup.select_one("li.next a")
        url = urljoin(site["url"], next_page["href"]) if next_page else None
        page_num += 1
        time.sleep(random.uniform(1, 3))

# ----- MAIN -----
def main():
    print("\n===== STARTING NEWS SCRAPING =====")
    for site in NEWS_SITES:
        scrape_news_site(site)

    print("\n===== STARTING E-COMMERCE SCRAPING =====")
    for site in ECOM_SITES:
        scrape_ecom_site(site)

if __name__ == "__main__":
    main()
