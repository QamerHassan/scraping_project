<p align="center">
  <img src="scraping_project_hero.png" alt="Scraping Project – Enterprise Web Intelligence Platform" width="100%" />
</p>

<h1 align="center">🕷️ Scraping Project</h1>

<p align="center">
  <strong>Enterprise-Grade Web Intelligence & Data Harvesting Platform</strong><br/>
  Multi-threaded · Anti-Block · Pagination · CSV/JSON Export · Email Alerts
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/BeautifulSoup4-Parsing-green?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Pandas-Data%20Processing-orange?style=for-the-badge&logo=pandas" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" />
</p>

---

## 🌐 About the Project

**Scraping Project** is a powerful, enterprise-ready web scraping and data intelligence platform engineered for **reliability, speed, and stealth**. Whether you're harvesting thousands of news articles or cataloging entire e-commerce stores, this platform handles it all — automatically, efficiently, and at scale.

Built with a modular architecture, it combines **multi-threaded parallel scraping**, **smart anti-block evasion**, and **automatic pagination traversal** to deliver clean, deduplicated datasets in both CSV and JSON formats. With optional **email notification alerts**, you stay informed the moment your scraping job completes — no babysitting required.

From news aggregation pipelines to product price monitoring systems, this tool forms the backbone of any serious data engineering workflow.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🗞️ **News Scraping** | Extracts headlines, links, and metadata from multiple news sources |
| 🛒 **E-Commerce Scraping** | Harvests product titles, prices, ratings, and links from online stores |
| ⚡ **Multi-threaded Execution** | Concurrent scraping with `ThreadPoolExecutor` for blazing-fast performance |
| 📄 **Auto Pagination** | Traverses all pages automatically — no manual URL management |
| 🛡️ **Anti-Block System** | Rotating user-agents, optional proxy support, and exponential backoff retries |
| 💾 **Dual Export** | Saves data to both **CSV** and **JSON** simultaneously |
| 🔁 **Deduplication** | Automatically removes duplicate entries by URL |
| 📧 **Email Alerts** | Sends a summary notification upon scraping completion |
| 📋 **Logging** | Detailed runtime logs saved to `scraping.log` for full auditability |

---

## 🗂️ Project Structure

```
scraping_project/
│
├── scrape_enterprise_anti_block.py  # 🏆 Main enterprise scraper with anti-block
├── scrape_all_pagination.py         # Pagination-focused scraper
├── scrape_all_robust.py             # Robust multi-site scraper
├── scrape_news.py                   # Dedicated news scraper
├── scrape_production.py             # Production-ready scraper
│
├── products.csv                     # Scraped e-commerce product data
├── news1.csv / news2.csv            # Scraped news data
├── scraping.log                     # Runtime log file
│
└── README.md
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/QamerHassan/scraping_project.git
cd scraping_project
```

### 2. Install Dependencies

```bash
pip install requests beautifulsoup4 pandas lxml tqdm
```

---

## ⚙️ Configuration

Open `scrape_enterprise_anti_block.py` and configure the `SITES` list to define your scraping targets:

```python
SITES = [
    {
        "type": "news",
        "url": "https://your-news-site.com/",
        "selector": "div.article h2",
        "filename": "news_output.csv"
    },
    {
        "type": "ecom",
        "url": "https://your-shop.com/products/",
        "product_selector": "div.product",
        "title_selector": "h2.name",
        "price_selector": "span.price",
        "rating_selector": "div.rating",
        "filename": "products_output.csv"
    }
]
```

### Optional: Enable Email Notifications

```python
EMAIL_ENABLED = True
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "recipient@gmail.com"
```

---

## ▶️ Usage

Run the enterprise scraper:

```bash
python scrape_enterprise_anti_block.py
```

Or use any specialized scraper:

```bash
python scrape_news.py
python scrape_all_pagination.py
python scrape_production.py
```

---

## 🛡️ Anti-Block Techniques

This scraper employs several stealth mechanisms to avoid detection and IP bans:

- **User-Agent Rotation** — Cycles through multiple browser fingerprints per request
- **Proxy Support** — Optionally routes requests through rotating proxies
- **Exponential Backoff** — Intelligently retries on rate limits (HTTP 429) with increasing wait times
- **Random Delays** — Inserts human-like pauses between requests (`0.3s – 1.0s`)

---

## 📊 Output Format

All scraped data is exported in **two formats** automatically:

**CSV** — Perfect for spreadsheets and data analysis tools
```
title, link, price, rating, source, scraped_at_utc
Book Title, https://..., £12.99, Three, https://books.toscrape.com, 2026-04-10 ...
```

**JSON (newline-delimited)** — Ideal for pipelines and APIs
```json
{"title": "Book Title", "link": "https://...", "price": "£12.99", "rating": "Three"}
```

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<p align="center">
  Built with 🕷️ precision and ⚡ power &nbsp;|&nbsp; <strong>Scraping Project</strong> &nbsp;|&nbsp; Enterprise Web Intelligence
</p>
