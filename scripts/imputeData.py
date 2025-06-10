import re
import os
import numpy as np
import pandas as pd
import logging

# —————————————————————————
# 0. SETUP LOGGING
# —————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# —————————————————————————
# 1. TEXT PREPROCESSING
# —————————————————————————
def preprocess(text):
    if pd.isna(text):
        return ""
    t = text.lower()
    t = t.replace("×", "x").replace("*", "x")
    t = re.sub(r'(?<=\d),(?=\d)', '.', t)       # 3,5m → 3.5m
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# —————————————————————————
# 2. COMPILED REGEXES
# —————————————————————————
dim_pair   = re.compile(r'(?P<w>\d+(?:\.\d+)?)\s*m?\s*[x×]\s*(?P<l>\d+(?:\.\d+)?)\s*m?')
width_re   = re.compile(r'ngang\s*(?P<w>\d+(?:\.\d+)?)\s*m')
length_re  = re.compile(r'(?:dài|dai)\s*(?P<l>\d+(?:\.\d+)?)\s*m')

bed_re     = re.compile(r'(?P<b>\d+)\s*(?:pn|phòng ngủ)')
bath_re    = re.compile(r'(?P<ba>\d+)\s*(?:wc|nhà vệ sinh)')

floor_l    = re.compile(r'(\d+)\s*lầu')
floor_tum  = re.compile(r'tum|gác')

dir_re     = re.compile(
    r'hướng\s*(đông bắc|tây nam|đông nam|tây bắc|đông|tây|nam|bắc)'
)

alley_w_re = re.compile(
    r'(?:hẻm|lộ|đường)[^\d]{0,5}(?P<aw>\d+(?:\.\d+)?)\s*m'
)

# —————————————————————————
# 3. EXTRACTION FUNCTION
# —————————————————————————
def extract(desc: str) -> pd.Series:
    text = preprocess(desc)

    # DIMENSIONS
    w = l = np.nan
    m = dim_pair.search(text)
    if m:
        w = float(m.group('w'))
        l = float(m.group('l'))
    else:
        m = width_re.search(text)
        if m: w = float(m.group('w'))
        m = length_re.search(text)
        if m: l = float(m.group('l'))

    # BED & BATH
    b = np.nan
    m = bed_re.search(text)
    if m: b = int(m.group('b'))

    ba = np.nan
    m = bath_re.search(text)
    if m: ba = int(m.group('ba'))

    # FLOORS
    floors = 0.0
    if 'trệt' in text:
        floors += 1
    floors += sum(int(n) for n in floor_l.findall(text))
    floors += 0.5 * len(floor_tum.findall(text))
    if floors == 0.0:
        floors = np.nan

    # DIRECTION
    direction = np.nan
    m = dir_re.search(text)
    if m:
        direction = m.group(1).title()

    # POSITION: only 'Đường chính' or 'Trong hẻm'
    if 'hẻm' in text:
        position = 'Trong hẻm'
    elif 'đường' in text:
        position = 'Đường chính'
    else:
        position = np.nan

    # ALLEY WIDTH
    alley_width = np.nan
    m = alley_w_re.search(text)
    if m:
        alley_width = float(m.group('aw'))

    # ROAD TYPE: restrict to four values
    if 'bê tông' in text:
        road_type = 'Đường bê tông'
    elif 'nhựa' in text:
        road_type = 'Đường nhựa'
    elif 'đường đất' in text:
        road_type = 'Đường đất'
    elif 'đường đá' in text:
        road_type = 'Đường đá'
    else:
        road_type = np.nan

    return pd.Series({
        'imputed_var_width': w,
        'imputed_var_length': l,
        'imputed_var_bedrooms': b,
        'imputed_var_bathrooms': ba,
        'imputed_var_floors': floors,
        'imputed_var_direction': direction,
        'imputed_var_position': position,
        'imputed_var_alley_width': alley_width,
        'imputed_var_road_type': road_type
    })

# —————————————————————————
# 4. MAIN PIPELINE
# —————————————————————————
def run():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    in_path = os.path.join(script_dir, "preprocessed-data", "guland_full.csv")
    out_path = os.path.join(script_dir, "preprocessed-data", "guland_full_imputed.csv")

    logging.info(f"Loading data from {in_path}")
    df = pd.read_csv(in_path, dtype=str)
    logging.info(f"Total rows: {len(df)}")

    logging.info("Starting extraction of imputed variables...")
    imputed = df['Description'].apply(extract)

    # Summary logs
    for col in imputed.columns:
        non_null = imputed[col].notna().sum()
        logging.info(f"{col}: {non_null}/{len(df)} non-null")

    df_out = pd.concat([df, imputed], axis=1)

    df_out.to_csv(out_path, index=False, encoding='utf-8-sig')
    logging.info(f"✅ Done! Saved with imputed vars to: {out_path}")

if __name__ == "__main__":
    run()
