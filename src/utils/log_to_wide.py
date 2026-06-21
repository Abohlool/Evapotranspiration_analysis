import pandas as pd
import glob
import os


def load_and_combine(data_dir, pattern="SensorData*.csv"):
    """
    Load and combine all matching CSV files.
    """
    os.chdir(data_dir)

    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} files")

    dfs = []
    for file in files:
        df = pd.read_csv(file, encoding="utf-8")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"Total combined rows: {len(combined):,}")
    
    return combined


def remove_duplicates(df):
    """
    Remove duplicates from DataFrame.
    """
    df = df.drop_duplicates(
        subset=["تاریخ و زمان", "گلخانه", "دستگاه", "نوع سنسور"],
        keep="first"
    )
    print(f"After removing duplicates: {len(df):,} rows")
    return df


def round_datetime(df):
    """
    Convert datetime and round to 10 minutes.
    """
    df["تاریخ و زمان"] = pd.to_datetime(df["تاریخ و زمان"])
    df["time_rounded"] = df["تاریخ و زمان"].dt.floor("10min")
    return df


def drop_columns(df):
    """
    Drop unnecessary columns.
    """
    df = df.drop(columns=["گلخانه", "دستگاه", "تاریخ و زمان", "واحد"])
    print(f"Kept columns: {list(df.columns)}")
    return df


def pivot_to_wide(df):
    """
    Pivot DataFrame to wide format.
    """
    wide = df.pivot_table(
        index="time_rounded",
        columns="نوع سنسور",
        values="مقدار",
        aggfunc="first"
    )

    wide = wide.reset_index()
    wide.columns.name = None

    print(f"\nWide format: {len(wide):,} rows × {len(wide.columns)} columns")
    print(f"Sensors: {wide.columns[1:].tolist()}")
    
    return wide


def save_csv(df, filename, data_dir):
    """
    Save DataFrame to CSV.
    """
    os.chdir(data_dir)
    df.to_csv(filename, index=False, encoding="utf-8-sig", quoting=1)
    print(f"\n✅ Saved to {filename}")
    print(f"   Rows: {len(df):,}")
    print(f"   File size: {os.path.getsize(filename):,} bytes")


def preview_data(df):
    """
    Preview the processed data.
    """
    print(f"\nFirst 5 rows:")
    print(df.head())


def make_wide(data_dir):
    """
    Main function to run the wide format conversion process.
    """
    df = load_and_combine(data_dir)
    df = remove_duplicates(df)
    df = round_datetime(df)
    df = drop_columns(df)
    wide = pivot_to_wide(df)
    save_csv(wide, "sensor_data_wide.csv", data_dir)
    preview_data(wide)
    return wide


if __name__ == "__main__":
    make_wide("../data")
