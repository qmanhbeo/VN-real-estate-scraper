# 🏠 Vietnam Real Estate Data Pipeline

This project scrapes and processes Vietnamese real estate listings from [Guland.vn](https://guland.vn), turning messy web listings into clean, analyzable CSV datasets.

Disclaimer: This project is a personal initiative and is not affiliated with any organization. It was originally created by the author to assist with his own research and real estate purchase decisions.

---

## 🚀 Quickstart

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

```bash
python scraper.py
```

This might take a really long while (~ 20 hours depending on the site)

### 4. Run the full pipeline

```bash
python main.py
```

---

## 📁 Project Structure

```
.
├── scraped-data/           # Raw listings, scraped per province
├── preprocessed-data/      # Cleaned, enriched data
├── scripts/                # Modular processing scripts (with run() functions)
│   ├── appendData.py       # Merges all scraped CSVs into one file
│   ├── cleanData.py        # Cleans formatting and structure
│   ├── imputeData.py       # Extracts dimensions, direction, road type from text
│   ├── preprocessData.py   # Converts prices, areas, time
│   └── descStats.py        # Summarizes data for inspection
├── scraper.py              # Scraper for Guland.vn
├── main.py                 # Runs everything in order
├── requirements.txt        # Required Python packages
└── README.md               # You’re here!
```

---

## ⚠️ Scraping Notice

**Use a VPN. Seriously.** Guland.vn may block your IP after a few thousand requests.

> ✅ What works:

* Using VPNs or rotating proxies
* Limiting scrape frequency (`time.sleep`)
* Only scraping provinces you need

> ❌ What gets you blocked:

* Running the scraper repeatedly with no delay
* Trying to pull all provinces in one go
* Ignoring headers or request throttling

---

## 📥 Sample Dataset

Want to see the results without scraping?

📦 Download a **sample cleaned dataset (real data)** here:
👉 [Kaggle: Vietnamese Real Estate Listings May 2024 (Cleaned)](https://www.kaggle.com/datasets/qmanhbeo/vietnamese-real-estate-listings-may-2024)

This includes:

* Title, price, area, location
* GPS coordinates
* Number of floors, bedrooms, bathrooms
* Road type, alley width
* Updated/scraped timestamps

---

## 🧠 How It Works

1. **`scraper.py`**: Scrapes each province/type combo and saves as CSVs
2. **`appendData.py`**: Merges all provincial files into one large CSV
3. **`imputeData.py`**: Uses regex to extract dimensions and features from listing descriptions
4. **`cleanData.py`**: Fixes weird values, trims whitespace, removes junk
5. **`preprocessData.py`**: Converts units, timestamps, and formats final output
6. **`descStats.py`**: Shows descriptive stats to help validate data quality

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
[LinkedIn](https://www.linkedin.com/in/mạnh-nguyễn/)
[ORCiD](https://orcid.org/0009-0009-0295-1508)
---

## 📄 License

This project is for **educational and research use only**.
Scraping real estate sites may violate their terms — use responsibly.
