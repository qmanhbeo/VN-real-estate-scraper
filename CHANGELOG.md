# 📜 Changelog

## 2025-09-12

### 🚀 Major Improvements
- Added **parallel scraping** with `scraper-parallel.py`
  - Uses multi-threading for detail pages → reduces runtime from ~20h to just a fraction.
- Added **incremental CSV writing** with `scraper-parallel-incrementCSV.py`
  - Saves data page-by-page instead of at the end.
  - Introduced per–listing ID checkpoints → prevents duplicate entries and allows seamless resume if interrupted.
  - All checkpoint files are now stored neatly in `scraped-data/checkpoint/`.
- Added last page identification using count of listings -> Avoid endless pagination

### ✅ Outcomes
- Scraper runs **much faster** (parallel workers configurable via `MAX_WORKERS`).
- Data is **more reliable** thanks to incremental writes + ID-level checkpoints.
- Accidental duplicate listings across pages are automatically removed.
- Repo structure is cleaner with a dedicated `checkpoint/` directory.

### 💡 Notes
- `scraper.py` (original single-threaded) is kept for stability/testing.
- `scraper-parallel.py` is fast but relies only on province–property checkpoints.
- `scraper-parallel-incrementCSV.py` is the recommended production scraper.

---
