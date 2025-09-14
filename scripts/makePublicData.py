import os
import pandas as pd
import logging

# —————————————————————————
# SETUP LOGGING
# —————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run():
    # same folder convention as preprocessData.py
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(script_dir, "preprocessed-data")
    infile  = os.path.join(folder, "guland_final.csv")
    outfile = os.path.join(folder, "guland_public.csv")

    logging.info(f"Loading data from {infile}")
    df = pd.read_csv(infile, dtype=str)

    logging.info("Dropping unnecessary columns...")
    df.drop(columns=["province_from_filename", "Images", "URL"], inplace=True, errors="ignore")

    logging.info("Converting 'Avatar' to binary indicator...")
    df["Avatar"] = df["Avatar"].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != "" else 0)

    logging.info("Saving to guland_public.csv...")
    df.to_csv(outfile, index=False, encoding="utf-8-sig")

    logging.info(f"✅ Public data saved to: {outfile}")

if __name__ == "__main__":
    run()
