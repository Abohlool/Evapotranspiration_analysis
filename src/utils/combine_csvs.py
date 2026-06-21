import pandas as pd
import glob
import os


def load_and_combine(data_dir, pattern="SensorData_*.csv"):
    """
    Load and combine all matching CSV files.
    """
    os.chdir(data_dir)
    
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} files:")
    for f in files:
        print(f"  {f} ({os.path.getsize(f):,} bytes)")

    dfs = []
    for file in files:
        df = pd.read_csv(file, encoding='utf-8')
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\n{'='*50}")
    print(f"Total combined rows: {len(combined):,}")
    
    return combined


def check_duplicates(df):
    """
    Check and report duplicate rows.
    """
    print(f"\nDuplicate rows (all columns identical): {df.duplicated().sum():,}")
    print(f"Duplicate rows (based on all columns except 'مقدار'): {df.duplicated(subset=['تاریخ و زمان', 'نوع سنسور', 'واحد']).sum():,}")
    print(f"Duplicate rows (based on date+device+sensor): {df.duplicated(subset=['تاریخ و زمان', 'نوع سنسور']).sum():,}")


def remove_duplicates(df):
    """
    Remove duplicates and return deduplicated DataFrame.
    """
    dedup_full = df.drop_duplicates(keep='first')
    print(f"\nAfter removing FULL duplicates: {len(dedup_full):,} rows")

    dedup_key = df.drop_duplicates(subset=['تاریخ و زمان', 'نوع سنسور', 'واحد'], keep='first')
    print(f"After removing duplicates (key columns): {len(dedup_key):,} rows")

    dedup_simple = df.drop_duplicates(subset=['تاریخ و زمان', 'نوع سنسور'], keep='first')
    print(f"After removing duplicates (date+device+sensor): {len(dedup_simple):,} rows")
    
    return dedup_key


def save_csv(df, filename, data_dir):
    """
    Save DataFrame to CSV.
    """
    os.chdir(data_dir)
    df.to_csv(filename, index=False, encoding='utf-8-sig', quoting=1)
    print(f"\n{'='*50}")
    print(f"✅ Saved to {filename}")
    print(f"   Final rows: {len(df):,}")
    print(f"   File size: {os.path.getsize(filename):,} bytes")


def preview_data(df):
    """
    Preview the data.
    """
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nLast 5 rows:")
    print(df.tail())
    print(f"\nDate range:")
    print(f"  Start: {df['تاریخ و زمان'].min()}")
    print(f"  End: {df['تاریخ و زمان'].max()}")


def combine_data(data_dir):
    """
    Main function to run the combine process.
    """
    combined = load_and_combine(data_dir)
    check_duplicates(combined)
    dedup = remove_duplicates(combined)
    save_csv(dedup, 'deduplicated.csv', data_dir)
    preview_data(dedup)
    return dedup


if __name__ == "__main__":
    combine_data("../data")
