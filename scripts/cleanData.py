import os
import re
import pandas as pd
import numpy as np
import logging

# —————————————————————————
# SETUP LOGGING
# —————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# —————————————————————————
# MAIN PIPELINE
# —————————————————————————
def run():
    # File paths
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    in_path = os.path.join(script_dir, "preprocessed-data", "guland_full_imputed.csv")
    out_path = os.path.join(script_dir, "preprocessed-data", "guland_full_imputed_cleaned.csv")

    logging.info(f"Loading data from {in_path}")
    df = pd.read_csv(in_path, dtype=str)
    total = len(df)
    logging.info(f"Total rows: {total}")

    # Columns mapping: original -> imputed
    merge_map = {
        'Width':          'imputed_var_width',
        'Length':         'imputed_var_length',
        'Bedrooms':       'imputed_var_bedrooms',
        'Bathrooms':      'imputed_var_bathrooms',
        'Floors':         'imputed_var_floors',
        'Position':       'imputed_var_position',
        'Direction':      'imputed_var_direction',
        'Alley Width':    'imputed_var_alley_width',
        'Road Type':      'imputed_var_road_type'
    }

    # Strip unit suffixes from original dimension columns
    for col in ['Width', 'Length', 'Alley Width']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r'(?i)m$', '', regex=True)

    # 2. Merge: use imputed ONLY when original is truly missing or invalid
    numeric_cols = ['Width', 'Length', 'Bedrooms', 'Bathrooms', 'Floors', 'Alley Width']
    for orig_col, imp_col in merge_map.items():
        if orig_col not in df or imp_col not in df:
            logging.warning(f"Missing column: {orig_col} or {imp_col}")
            continue

        orig = df[orig_col].copy()
        imp  = df[imp_col]

        if orig_col in numeric_cols:
            # consider non-numeric or NaN as missing
            mask_orig_invalid = pd.to_numeric(orig, errors='coerce').isna()
            use_imp = mask_orig_invalid & imp.notna()
        else:
            s = orig.astype(str).str.strip().str.lower()
            mask_orig_empty = orig.isna() | s.eq('') | s.eq('nan')
            use_imp = mask_orig_empty & imp.notna()

        filled = use_imp.sum()
        # overwrite only masked rows
        df[orig_col] = orig.where(~use_imp, imp.astype(str))
        logging.info(f"{orig_col}: filled {filled}/{total} from {imp_col}")

    # 3. Convert to appropriate dtypes
    # Numeric dims
    for col in ['Width', 'Length', 'Alley Width']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Integral counts
    df['Bedrooms'] = pd.to_numeric(df['Bedrooms'], errors='coerce').astype('Int64')
    df['Bathrooms'] = pd.to_numeric(df['Bathrooms'], errors='coerce').astype('Int64')
    # Floors may be non-integer
    df['Floors'] = pd.to_numeric(df['Floors'], errors='coerce')

    # 4. Drop imputed columns
    df.drop(columns=list(merge_map.values()), inplace=True)

    # 5. Save
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    logging.info(f"✅ Cleaned data saved to: {out_path}")

if __name__ == '__main__':
    run()
