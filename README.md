# 🏠 Vietnam Real Estate Data Pipeline

This project scrapes and processes Vietnamese real estate listings from a publicly accessible site, turning messy web listings into clean, analyzable CSV datasets.

*Disclaimer: Personal initiative; not affiliated with any organization. Originally built to support the author's research and purchase decisions.*

---

## 🚀 Quickstart

**Runtime:** Developed with Python 3.10.6
✅ Recommended: Python 3.10+
⚠️ Minimum: Python 3.8+

### 1) Clone

```bash
git clone https://github.com/qmanhbeo/VN-real-estate-scraper.git
cd VN-real-estate-scraper
```

### 2) Install deps

```bash
pip install -r requirements.txt
```

### 3) Scrape (standalone)

You have **three options** depending on speed and reliability:

* **`scraper-parallel-incrementCSV.py`** → ✅ **Recommended (active)**
  *Fast + resilient.* Writes incrementally, deduplicates by listing ID, and keeps per‑listing checkpoints.

* **Legacy (kept for reference / fallback):**

  * `_legacy_scraper/scraper.py` → single‑threaded, *very stable but slow (\~40h for all provinces)*
  * `_legacy_scraper/scraper-parallel.py` → early parallel version, *faster but less robust than the recommended script*

Run the recommended one:

```bash
python scraper-parallel-incrementCSV.py
```

### 4) (Optional) ⚙️ Performance tuning

* **`province_slugs`**: limit to target provinces
* **`property_types`**: restrict listing categories
* **`MAX_WORKERS`**: 8–16 = sweet spot
* **`PAGE_SLEEP`**: increase if you encounter 429/403

### 5) Full cleaning & preprocessing pipeline

```bash
python main.py
```

This will:

* Merge raw CSVs → **`preprocessed-data/guland_full.csv`** (name may vary)
* Impute/clean fields
* Convert price/area/time → **`preprocessed-data/guland_final.csv`**
* Generate quick descriptive stats

### 6) 🛍️ Publish a public‑safe dataset (PII‑reduced)

Either run the full pipeline (Step 5) which **already** includes this as the final step, **or** run the publish step standalone:

```bash
python -m scripts.makePublicData
```

It produces **`preprocessed-data/guland_public.csv`** by:

* Dropping: `province_from_filename`, `Images`, `URL`
* Converting `Avatar` → **1** if non‑empty, **0** if empty
* Keeping the rest (e.g., `Title`, `Description`, `Location`, `Agent Name`, etc.)

---

## 📁 Project Structure

```
.
├── scraped-data/                         # Raw listings per province
│   ├── hanoi.csv
│   ├── tp-ho-chi-minh.csv
│   ├── failed.log
│   └── checkpoint/
│       ├── done.log
│       └── *_ids.log
├── preprocessed-data/                    # Cleaned/processed outputs
│   ├── guland_final.csv
│   └── guland_public.csv
├── scripts/                              # Modular processing (each has run())
│   ├── appendData.py
│   ├── cleanData.py
│   ├── imputeData.py
│   ├── preprocessData.py
│   ├── descStats.py
│   └── makePublicData.py                 # <-- NEW: builds guland_public.csv
├── _legacy_scraper/                      # <-- Legacy scrapers (kept for reference)
│   ├── scraper.py
│   └── scraper-parallel.py
├── scraper-parallel-incrementCSV.py      # <-- Active recommended scraper
├── main.py                               # Runs the full pipeline (incl. publish)
├── requirements.txt
└── README.md
```

---

## ⚠️ Scraping Notice

**Use a VPN — seriously.** The site may block your IP after a few thousand requests.

**Works:** VPNs / rotating proxies (e.g., 1.1.1.1 by WARP), polite delays, limiting provinces/types.
**Gets blocked:** hammering all provinces with no delay, rerunning too quickly, ignoring headers/throttling.

---

## 📥 Sample Dataset

Want to see results without scraping?

📦 **Sample cleaned dataset (real data)** on Kaggle:
[Vietnamese Real Estate Listings (Cleaned)](https://www.kaggle.com/datasets/qmanhbeo/vietnamese-real-estate-listings-may-2024)
(includes title/price/area/location, GPS, floors/bedrooms/bathrooms, road type, alley width, updated/scraped timestamps)

---

## 🧠 Pipeline Components

1. **`scraper-parallel-incrementCSV.py`** (active): scrape with incremental writes + ID checkpoints
2. **`scripts/appendData.py`**: merge all CSVs
3. **`scripts/imputeData.py`**: regex‑extract dimensions + features
4. **`scripts/cleanData.py`**: normalize + fix oddities
5. **`scripts/preprocessData.py`**: convert price/area/time → `guland_final.csv`
6. **`scripts/descStats.py`**: quick descriptive stats
7. **`scripts/makePublicData.py`**: **publish** → `guland_public.csv` (drop sensitive columns, binarize Avatar)

> Legacy scrapers live in `_legacy_scraper/` for archival and comparison.

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
[LinkedIn](https://www.linkedin.com/in/qmanhbeo/) · [ORCiD](https://orcid.org/0009-0009-0295-1508)

---

## 📄 License

This project is for **educational and research use only**.
Scraping real estate sites may violate their terms — use responsibly.
