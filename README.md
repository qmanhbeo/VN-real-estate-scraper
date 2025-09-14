# 🏠 Vietnam Real Estate Data Pipeline

This project scrapes and processes Vietnamese real estate listings from a publicly accessible Vietnamese real estate site, turning messy web listings into clean, analyzable CSV datasets.

Disclaimer: This project is a personal initiative and is not affiliated with any organization. It was originally created by the author to assist with his own research and real estate purchase decisions.

---

## 🚀 Quickstart

**Runtime:** Developed with Python 3.10.6.  
✅ Recommended: Python 3.10+  
⚠️ Minimum: Python 3.8+

### 1. Clone this repository

```bash
git clone https://github.com/qmanhbeo/VN-real-estate-scraper.git
cd VN-real-estate-scraper
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the scraper as a standalone

You have **three options** depending on speed and reliability:

* **`scraper.py`** → the original, single-threaded scraper.
  *Very stable but very slow (\~40 hours for all provinces).*

* **`scraper-parallel.py`** → parallelized scraper using multiple threads.
  *Much faster (proportional to number of workers), same output format. Uses a global province–property checkpoint.*

* **`scraper-parallel-incrementCSV.py`** → parallel scraper with incremental CSV writing and per-listing checkpoints.
  *Newest option: progress is saved page-by-page, duplicates are avoided by logging listing IDs, and all checkpoints are stored in a dedicated folder.*

Recommended: Use scraper-parallel-incrementCSV.py (fastest + safest). The others are kept for comparison or fallback. Example:

```bash
python scraper-parallel-incrementCSV.py
```

### 4. (Optional) ⚙️ Performance Tuning

You can tweak desired output and speed vs. politeness in the scraper configs:

- **`province_slugs`**: change to desired provinces
- **`property_types`**: change to desired property types
- **`MAX_WORKERS`**: concurrency for detail pages.
  - 8–16 = safe, respectful, and sweet spot; >20 gives diminishing returns.
- **`PAGE_SLEEP`**: pause between listing pages (seconds).
  - Lower = faster but riskier; raise if you get 429/403 errors.


### 5. Run the full dataset cleaning and preprocessing pipeline

```bash
python main.py
```

---

## 📁 Project Structure

```
.
├── scraped-data/           # Raw listings, scraped per province
│   ├── hanoi.csv
│   ├── tp-ho-chi-minh.csv
│   ├── failed.log          # Provinces/types that failed mid-run
│   └── checkpoint/         # Checkpoint files
│       ├── done.log        # Province|property combos already scraped
│       ├── hanoi_dat-tho-cu_ids.log
│       ├── tp-ho-chi-minh_can-ho-chung-cu_ids.log
│       └── ...
├── preprocessed-data/      # Cleaned, enriched data
├── scripts/                # Modular processing scripts (with run() functions)
│   ├── appendData.py       # Merges all scraped CSVs into one file
│   ├── cleanData.py        # Cleans formatting and structure
│   ├── imputeData.py       # Extracts dimensions, direction, road type from text
│   ├── preprocessData.py   # Converts prices, areas, time
│   └── descStats.py        # Summarizes data for inspection
├── scraper.py              # Single-threaded scraper
├── scraper-parallel.py     # Parallel scraper
├── scraper-parallel-incrementCSV.py  # Parallel scraper w/ incremental writes + ID checkpoints
├── main.py                 # Runs everything in order
├── requirements.txt        # Required Python packages
└── README.md               # You’re here!
```

---

## ⚠️ Scraping Notice

**Use a VPN. Seriously.** The website may block your IP after a few thousand requests.

> ✅ What works:
>
> * Using VPNs or rotating proxies (I recommend Warp's 1.1.1.1. It's free and easy to use)
> * Limiting scrape frequency (`time.sleep`)
> * Only scraping provinces you need
>
> ❌ What gets you blocked:
>
> * Running the scraper repeatedly with no delay
> * Trying to pull all provinces in one go
> * Ignoring headers or request throttling

---

## 📥 Sample Dataset

Want to see the results without scraping?

📦 Download a **sample cleaned dataset (real data)** here:
👉 [Kaggle: Vietnamese Real Estate Listings May 2025 (Cleaned)](https://www.kaggle.com/datasets/qmanhbeo/vietnamese-real-estate-listings-may-2024)

This includes:

* Title, price, area, location
* GPS coordinates
* Number of floors, bedrooms, bathrooms
* Road type, alley width
* Updated/scraped timestamps

---

## 🧠 What Components in Pipeline do

1. **`scraper.py`**: Scrapes each province/type combo and saves as CSVs.
2. **`appendData.py`**: Merges all provincial files into one large CSV.
3. **`imputeData.py`**: Uses regex to extract dimensions and features from listing descriptions.
4. **`cleanData.py`**: Fixes weird values, trims whitespace, removes junk.
5. **`preprocessData.py`**: Converts units, timestamps, and formats final output.
6. **`descStats.py`**: Shows descriptive stats to help validate data quality.

You can run any step individually (each has a `run()` function), or run the whole thing using `main.py`.

---

## 📆 requirements.txt

```txt
pandas
numpy
requests
beautifulsoup4
tqdm
```

---

## 🧑‍💼 Author

**Nguyễn Quang Mạnh**
[LinkedIn](https://www.linkedin.com/in/qmanhbeo/)
[ORCiD](https://orcid.org/0009-0009-0295-1508)

---

## 📄 License

This project is for **educational and research use only**.
Scraping real estate sites may violate their terms — use responsibly.
