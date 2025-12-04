import os
import pandas as pd
import glob

# Configuration
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

def clean_weather_data():
    csv_files = glob.glob(os.path.join(RAW_DATA_DIR, "weather_waterloo_*.csv"))

    dfs = []
    for f in csv_files:
        df = pd.read_csv(f)
        dfs.append(df)
    full_df = pd.concat(dfs, ignore_index=True)

    # Parse dates
    full_df['Date/Time (LST)'] = pd.to_datetime(full_df['Date/Time (LST)'])
    full_df = full_df.sort_values('Date/Time (LST)')

    # Set index to datetime
    full_df = full_df.set_index('Date/Time (LST)')

    # Reindex to ensure complete hourly range
    all_hours = pd.date_range(start=full_df.index.min(), end=full_df.index.max(), freq='H')
    full_df = full_df.reindex(all_hours)

    # Interpolate Temp
    full_df['Temp (°C)'] = full_df['Temp (°C)'].interpolate(method='linear')

    # Fill Precip with 0
    full_df['Precip. Amount (mm)'] = full_df['Precip. Amount (mm)'].fillna(0)

    # Reset index and rename
    full_df = full_df.reset_index().rename(columns={'index': 'DateTime'})

    # Select only relevant columns
    cols_to_keep = ['DateTime', 'Year', 'Month', 'Day', 'Time (LST)', 'Temp (°C)', 'Precip. Amount (mm)']
    full_df['Year'] = full_df['DateTime'].dt.year
    full_df['Month'] = full_df['DateTime'].dt.month
    full_df['Day'] = full_df['DateTime'].dt.day
    full_df['Time (LST)'] = full_df['DateTime'].dt.strftime('%H:%M')

    final_df = full_df[cols_to_keep]

    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)
    output_path = os.path.join(PROCESSED_DATA_DIR, "weather_clean.csv")
    final_df.to_csv(output_path, index=False)
    print(f"Cleaned weather data saved at {output_path}")

def main():
    clean_weather_data()

if __name__ == "__main__":
    main()
