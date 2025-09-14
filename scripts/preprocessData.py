import re
from datetime import timedelta
import pandas as pd
import logging
import os

# —————————————————————————
# SETUP LOGGING
# —————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# —————————————————————————
# HELPERS
# —————————————————————————

def parse_price_to_million(text: str) -> float:
    t = str(text).strip().lower()
    m = re.search(r'([0-9]+(?:\.[0-9]+)?)', t)
    if not m:
        return pd.NA
    v = float(m.group(1))
    if 'tỷ' in t:
        return v * 1000
    if 'triệu' in t:
        return v
    return pd.NA


def parse_area(text: str) -> float:
    t = str(text).strip().lower()
    t = re.sub(r'm²|m2$', '', t)
    try:
        return float(t)
    except:
        return pd.NA


def parse_relative_to_timedelta(text: str) -> pd.Timedelta:
    t = str(text).strip().lower()
    m = re.match(r"(\d+)\s*(tháng|tuần|ngày|giờ|phút|giây) trước", t)
    if not m:
        return timedelta(0)
    num, unit = int(m.group(1)), m.group(2)
    if unit == 'tháng':   return timedelta(days=30 * num)
    if unit == 'tuần':    return timedelta(weeks=num)
    if unit == 'ngày':    return timedelta(days=num)
    if unit == 'giờ':     return timedelta(hours=num)
    if unit == 'phút':    return timedelta(minutes=num)
    if unit == 'giây':    return timedelta(seconds=num)
    return timedelta(0)

# —————————————————————————
# MAIN PIPELINE
# —————————————————————————

def run():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(script_dir, "preprocessed-data")
    infile  = folder + "\\guland_full_imputed_cleaned.csv"
    outfile = folder + "\\guland_final.csv"

    logging.info(f"Loading data from {infile}")
    df = pd.read_csv(infile, dtype=str)
    logging.info(f"Total rows: {len(df)}")

    # 1) Price
    logging.info("Converting Price to million...")
    df['Price'] = df['Price'].apply(parse_price_to_million)
    df = df.dropna(subset=['Price'])

    # 2) Area
    logging.info("Parsing Area to numeric...")
    df['Area'] = df['Area'].apply(parse_area)

    # 3) Last Updated Date
    logging.info("Parsing 'Scraped At' to datetime with correct format...")
    def parse_scraped_at(s):
        if pd.isna(s): return pd.NaT
        s = s.strip()
        # ISO format yyyy-mm-dd hh:mm:ss
        m_iso = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:?\d{0,2})", s)
        if m_iso:
            try:
                return pd.to_datetime(s, format='%Y-%m-%d %H:%M:%S', errors='coerce')
            except:
                return pd.to_datetime(s, format='%Y-%m-%d %H:%M', errors='coerce')
        # d/m/yyyy hh:mm
        return pd.to_datetime(s, dayfirst=True, errors='coerce')

    df['Scraped At DT'] = df['Scraped At'].apply(parse_scraped_at)

    logging.info("Parsing 'Last Updated' to timedelta...")
    df['Delta'] = df['Last Updated'].apply(parse_relative_to_timedelta)

    logging.info("Computing 'Last Updated Date'...")
    df['Last Updated Date DT'] = df['Scraped At DT'] - df['Delta']

    # Debug sample
    debug = df.loc[:3, ['Scraped At', 'Last Updated', 'Scraped At DT', 'Delta', 'Last Updated Date DT']]
    logging.info("Sample computations:\n%s", debug.to_string(index=False))

    logging.info("Formatting 'Last Updated Date' to dd/MM/YYYY HH:mm...")
    df['Last Updated Date'] = df['Last Updated Date DT'].dt.strftime('%d/%m/%Y %H:%M')

    # cleanup
    df.drop(columns=['Scraped At DT', 'Delta', 'Last Updated Date DT'], inplace=True)

    # 4) Save
    df.to_csv(outfile, index=False, encoding='utf-8-sig')
    logging.info(f"✅ Final data saved to: {outfile}")

if __name__ == '__main__':
    run()
