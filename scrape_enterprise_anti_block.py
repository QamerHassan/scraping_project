# scrape_enterprise_anti_block.py
import os
import time
import random
import smtplib
from email.message import EmailMessage
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging

# ------------------- CONFIG -------------------
# User-Agent rotation list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 Chrome/140.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/605.1.15",
]

# Proxy list (optional, update with working proxies)
PROXIES = [
    # "http://user:pass@ip:port",
    # "http://ip:port",
]

SITES = [
    {"type": "news", "url": "https://quotes.toscrape.com/", "selector": "div.quote span.text", "filename": "news1.csv"},
    {"type": "news", "url": "https://quotes.toscrape.com/page/2/", "selector": "div.quote span.text", "filename": "news2.csv"},
    {"type": "ecom", "url": "https://books.toscrape.com/catalogue/page-1.html",
     "product_selector": "article.product_pod",
     "title_selector": "h3 a",
     "price_selector": "p.price_color",
     "rating_selector": "p.star-rating",
     "filename": "products.csv"}
]

OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

LOG_FILE = "scraping.log"
logging.basicConfig(filename=LOG_FILE, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Email notification config
EMAIL_ENABLED = False
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "yourpassword"
EMAIL_RECEIVER = "receiveremail@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ------------------- FUNCTIONS -------------------
def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def get_random_proxy():
    if not PROXIES:
        return None
    return {"http": random.choice(PROXIES), "https": random.choice(PROXIES)}

def fetch_html(url, retries=3, backoff=2):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=get_random_headers(), proxies=get_random_proxy(), timeout=10)
            if r.status_code == 429:  # Too many requests
                logging.warning(f"Rate limit hit for {url}, sleeping...")
                time.sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt} failed for {url}: {e}")
            time.sleep(backoff + random.uniform(0.5, 1.5))
            backoff *= 2
    logging.error(f"Skipping {url} after {retries} attempts")
    return None

# ------------------- NEWS -------------------
def scrape_news_page(url, selector, base_url):
    html = fetch_html(url)
    if html is None:
        return [], None
    soup = BeautifulSoup(html, "lxml")
    items = [{"title": el.get_text(strip=True),
              "link": urljoin(base_url, el.find_parent("a").get("href")) if el.find_parent("a") else url,
              "source": base_url} for el in soup.select(selector)]
    next_page_tag = soup.select_one("li.next a")
    next_url = urljoin(base_url, next_page_tag["href"]) if next_page_tag else None
    return items, next_url

def scrape_news(site):
    url = site["url"]
    selector = site["selector"]
    filename = os.path.join(OUTPUT_FOLDER, site["filename"])
    all_items = []

    logging.info(f"Starting news scraping: {url}")
    pbar = tqdm(desc=f"[News] {filename}", unit="page")

    urls_to_scrape = [url]
    with ThreadPoolExecutor(max_workers=5) as executor:
        while urls_to_scrape:
            future_to_url = {executor.submit(scrape_news_page, u, selector, site["url"]): u for u in urls_to_scrape}
            urls_to_scrape = []
            for future in as_completed(future_to_url):
                try:
                    items, next_url = future.result()
                    all_items.extend(items)
                    if next_url:
                        urls_to_scrape.append(next_url)
                    pbar.update(1)
                    time.sleep(random.uniform(0.3, 1.0))
                except Exception as e:
                    logging.error(f"Error scraping page: {e}")
    pbar.close()

    df = pd.DataFrame(all_items)
    df.drop_duplicates(subset=["link"], inplace=True)
    df["scraped_at_utc"] = pd.Timestamp.utcnow()
    df.to_csv(filename, index=False)
    df.to_json(filename.replace(".csv", ".json"), orient="records", lines=True)
    logging.info(f"[News] Completed {filename}, total items: {len(df)}")
    return len(df)

# ------------------- E-COMMERCE -------------------
def scrape_ecom_page(url, product_sel, title_sel, price_sel, rating_sel, base_url):
    html = fetch_html(url)
    if html is None:
        return [], None
    soup = BeautifulSoup(html, "lxml")
    items = []
    for product in soup.select(product_sel):
        title_tag = product.select_one(title_sel)
        title = title_tag["title"] if title_tag else ""
        link = urljoin(base_url, title_tag["href"]) if title_tag else url
        price = product.select_one(price_sel).get_text(strip=True) if product.select_one(price_sel) else ""
        rating_tag = product.select_one(rating_sel)
        rating = rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else ""
        items.append({"title": title, "link": link, "price": price, "rating": rating, "source": base_url})
    next_page_tag = soup.select_one("li.next a")
    next_url = urljoin(base_url, next_page_tag["href"]) if next_page_tag else None
    return items, next_url

def scrape_ecom(site):
    url = site["url"]
    filename = os.path.join(OUTPUT_FOLDER, site["filename"])
    all_items = []

    logging.info(f"Starting e-commerce scraping: {url}")
    pbar = tqdm(desc=f"[Ecom] {filename}", unit="page")

    urls_to_scrape = [url]
    with ThreadPoolExecutor(max_workers=5) as executor:
        while urls_to_scrape:
            future_to_url = {executor.submit(scrape_ecom_page, u, site["product_selector"], site["title_selector"],
                                             site["price_selector"], site["rating_selector"], site["url"]): u for u in urls_to_scrape}
            urls_to_scrape = []
            for future in as_completed(future_to_url):
                try:
                    items, next_url = future.result()
                    all_items.extend(items)
                    if next_url:
                        urls_to_scrape.append(next_url)
                    pbar.update(1)
                    time.sleep(random.uniform(0.3, 1.0))
                except Exception as e:
                    logging.error(f"Error scraping page: {e}")
    pbar.close()

    df = pd.DataFrame(all_items)
    df.drop_duplicates(subset=["link"], inplace=True)
    df["scraped_at_utc"] = pd.Timestamp.utcnow()
    df.to_csv(filename, index=False)
    df.to_json(filename.replace(".csv", ".json"), orient="records", lines=True)
    logging.info(f"[Ecom] Completed {filename}, total products: {len(df)}")
    return len(df)

# ------------------- EMAIL -------------------
def send_email(subject, body):
    if not EMAIL_ENABLED:
        return
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info("Email notification sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# ------------------- MAIN -------------------
def main():
    logging.info("==== Scraping Started ====")
    results = {}

    with ThreadPoolExecutor(max_workers=len(SITES)) as executor:
        future_to_site = {}
        for site in SITES:
            if site["type"] == "news":
                future = executor.submit(scrape_news, site)
            elif site["type"] == "ecom":
                future = executor.submit(scrape_ecom, site)
            future_to_site[future] = site["filename"]

        for future in as_completed(future_to_site):
            filename = future_to_site[future]
            try:
                count = future.result()
                results[filename] = count
                logging.info(f"[DONE] {filename} scraped {count} items/products")
            except Exception as exc:
                logging.error(f"[ERROR] {filename} generated exception: {exc}")

    logging.info("==== Scraping Finished ====")

    # Send email summary
    body = "Scraping completed successfully!\n\n"
    for file, count in results.items():
        body += f"{file}: {count} items/products scraped\n"
    send_email("Scraping Completed", body)

if __name__ == "__main__":
    main()
