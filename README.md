# Scraping Project

This project is a **robust and efficient web scraper** for scraping news sites and e-commerce websites. It is designed to handle pagination, retries, and anti-block techniques, and stores the scraped data in CSV and JSON formats.

---

## Features

- Scrapes multiple **news websites** and **e-commerce websites**.
- Handles **pagination** automatically.
- **Multi-threaded** scraping for faster performance.
- **Anti-block features**:
  - Random user-agents
  - Optional proxies
  - Retry mechanism with exponential backoff
- Saves **partial results** to CSV/JSON to avoid data loss.
- Deduplicates entries automatically.
- Optional **email notification** after scraping.

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/YOUR_USERNAME/scraping_project.git
cd scraping_project
