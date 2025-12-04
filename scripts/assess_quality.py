import os
import pandas as pd
import glob

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
GTFS_DIR = os.path.join(DATA_DIR, 'gtfs')
DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

def assess_gtfs():
    report = []
    report.append("# GTFS Quality Assessment\n")

    required_files = ['agency.txt', 'stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt', 'calendar_dates.txt']

    for file in required_files:
        path = os.path.join(GTFS_DIR, file)
        if os.path.exists(path):
            df = pd.read_csv(path)
            report.append(f"- **{file}**: Found. {len(df)} records.")
            if file == 'trips.txt':
                if 'trip_id' not in df.columns or 'route_id' not in df.columns or 'service_id' not in df.columns:
                    report.append(f"  - [WARNING] Missing required columns in {file}.")
            if file == 'stop_times.txt':
                if 'trip_id' not in df.columns or 'stop_id' not in df.columns or 'arrival_time' not in df.columns:
                    report.append(f"  - [WARNING] Missing required columns in {file}.")

        else:
            report.append(f"- **{file}**: [MISSING]")
    return "\n".join(report)

def assess_weather():
    report = []
    report.append("\n# Weather Quality Assessment\n")

    csv_files = glob.glob(os.path.join(DATA_DIR, "weather_waterloo_*.csv"))
    if not csv_files:
        report.append("- [ERROR] No weather CSV files found.")
        return "\n".join(report)

    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            report.append(f"- [ERROR] Failed to read {os.path.basename(f)}: {e}")      
    if not dfs:
        return "\n".join(report)

    full_df = pd.concat(dfs, ignore_index=True)

    # Check columns
    required_cols = ['Date/Time (LST)', 'Temp (°C)', 'Precip. Amount (mm)']
    for col in required_cols:
        if col not in full_df.columns:
            report.append(f"- [ERROR] Missing column: {col}")

    if 'Date/Time (LST)' in full_df.columns:
        full_df['dt'] = pd.to_datetime(full_df['Date/Time (LST)'])
        full_df = full_df.sort_values('dt')

        # Check for gaps
        min_date = full_df['dt'].min()
        max_date = full_df['dt'].max()
        expected_range = pd.date_range(start=min_date, end=max_date, freq='H')
        missing_timestamps = expected_range.difference(full_df['dt'])

        report.append(f"- **Time Range**: {min_date} to {max_date}")
        report.append(f"- **Total Records**: {len(full_df)}")
        report.append(f"- **Missing Timestamps**: {len(missing_timestamps)} hours missing from sequence.")

        # Check missing values
        if 'Temp (°C)' in full_df.columns:
            missing_temp = full_df['Temp (°C)'].isnull().sum()
            report.append(f"- **Missing Temp (°C)**: {missing_temp} ({missing_temp/len(full_df)*100:.2f}%)")

        if 'Precip. Amount (mm)' in full_df.columns:
            missing_precip = full_df['Precip. Amount (mm)'].isnull().sum()
            report.append(f"- **Missing Precip. Amount (mm)**: {missing_precip} ({missing_precip/len(full_df)*100:.2f}%)")

    return "\n".join(report)

def main():
    gtfs_report = assess_gtfs()
    weather_report = assess_weather()

    full_report = gtfs_report + "\n" + weather_report
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    report_path = os.path.join(DOCS_DIR, "quality_report.md")
    with open(report_path, "w") as f:
        f.write(full_report)

    print(f"Quality report saved at {report_path}")
    print(full_report)

if __name__ == "__main__":
    main()
