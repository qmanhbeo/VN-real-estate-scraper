import os
import pandas as pd

def run():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(script_dir, "scraped-data")
    output_path = os.path.join(script_dir, "preprocessed-data")
    os.makedirs(output_path, exist_ok=True)

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    all_dataframes = []
    qc_report = []

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path)

            province = file.replace('.csv', '')
            df['province_from_filename'] = province

            num_rows = len(df)
            num_missing = df.isna().sum().sum()
            is_empty = df.empty or df.isna().all(axis=1).all()

            qc_report.append({
                'file': file,
                'rows': num_rows,
                'missing_values': num_missing,
                'is_empty_or_all_NaN': is_empty
            })

            if not is_empty:
                all_dataframes.append(df)

            print(f"✅ Loaded {file} ({num_rows} rows, {num_missing} missing)")
            if is_empty:
                print(f"   ⚠️  {file} appears empty or invalid")

        except Exception as e:
            print(f"❌ Failed to load {file}: {e}")
            qc_report.append({
                'file': file,
                'rows': 0,
                'missing_values': 'ERROR',
                'is_empty_or_all_NaN': True
            })

    # Save the QC report
    qc_df = pd.DataFrame(qc_report)
    qc_df.to_csv(os.path.join(output_path, "guland_qc_report.csv"), index=False)

    # Combine valid data
    if all_dataframes:
        full_df = pd.concat(all_dataframes, ignore_index=True)
        full_df.to_csv(os.path.join(output_path, "guland_full.csv"), index=False, encoding='utf-8-sig')
        print(f"\n🎉 Appended {len(all_dataframes)} files. Output: guland_full.csv")
    else:
        print("\n❌ No valid data to append!")

    print(f"📝 QC report saved to guland_qc_report.csv")

if __name__ == "__main__": run() 