import logging
import pandas as pd
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
# MAIN PIPELINE
# —————————————————————————

def run():
    # File path
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    infile = os.path.join(script_dir, "preprocessed-data", "guland_final.csv")

    logging.info(f"Loading dataset from {infile}")
    df = pd.read_csv(infile)
    n_rows, n_cols = df.shape
    logging.info(f"Total rows: {n_rows}, Total columns: {n_cols}")

    # 1. Missingness summary
    logging.info("Computing missingness per column...")
    missing = df.isna().sum().to_frame(name='missing_count')
    missing['missing_pct'] = (missing['missing_count'] / n_rows * 100).round(2)
    logging.info(f"Missingness summary:\n{missing}")

    # 2. Numeric descriptive statistics
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    logging.info(f"Numeric columns detected: {numeric_cols}")
    if numeric_cols:
        desc = df[numeric_cols].describe().T
        logging.info(f"Numeric descriptive statistics:\n{desc}")
    else:
        logging.info("No numeric columns to describe.")

    # 3. Categorical value counts for key columns
    cat_cols = ['Position', 'Direction', 'Road Type', 'Property Type', 'Province']
    for col in cat_cols:
        if col in df.columns:
            logging.info(f"Value counts for {col} (top 10):\n{df[col].value_counts(dropna=False).head(10)}")
        else:
            logging.warning(f"Column {col} not found in dataset.")

    # 4. Area and Price distributions (quartiles)
    for col in ['Price', 'Area']:
        if col in df.columns:
            stats = df[col].describe()[['min','25%','50%','75%','max']]
            logging.info(
                f"{col} distribution - min: {stats['min']}, 25%: {stats['25%']}, "
                f"50%: {stats['50%']}, 75%: {stats['75%']}, max: {stats['max']}"
            )

    logging.info("Analysis complete.")

if __name__ == '__main__':
    run()
