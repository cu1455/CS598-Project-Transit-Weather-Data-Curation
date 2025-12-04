import os
import pandas as pd
import glob

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
GTFS_DIR = os.path.join(DATA_DIR, 'gtfs')
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
FINAL_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'final')

def load_gtfs():
    stop_times = pd.read_csv(os.path.join(GTFS_DIR, 'stop_times.txt'))
    trips = pd.read_csv(os.path.join(GTFS_DIR, 'trips.txt'))
    calendar_dates = pd.read_csv(os.path.join(GTFS_DIR, 'calendar_dates.txt'))
    return stop_times, trips, calendar_dates

def process_transit_data(stop_times, trips, calendar_dates):
    calendar_dates['date'] = pd.to_datetime(calendar_dates['date'], format='%Y%m%d')

    """
    Weather data (Dec 2025) is not available, so shift dates back by 1 year to match available weather data (2024)
    This is just a simulation of the real data to demonstrate the pipeline
    To obtain the correct integrated dataset, one needs to collect the data in Dec 2025 (which is not available at the time of this writing)
    """
    calendar_dates['date'] = calendar_dates['date'] - pd.DateOffset(years=1)

    stop_times['hour_str'] = stop_times['arrival_time'].str.split(':').str[0].astype(int)
    merged = stop_times[['trip_id', 'hour_str']].merge(trips[['trip_id', 'service_id']], on='trip_id')
    hourly_counts_by_service = merged.groupby(['service_id', 'hour_str']).size().reset_index(name='stop_count')
    daily_counts = hourly_counts_by_service.merge(calendar_dates[['service_id', 'date']], on='service_id')
    mask = daily_counts['hour_str'] >= 24
    daily_counts.loc[mask, 'date'] = daily_counts.loc[mask, 'date'] + pd.Timedelta(days=1)
    daily_counts.loc[mask, 'hour_str'] = daily_counts.loc[mask, 'hour_str'] - 24

    final_transit_counts = daily_counts.groupby(['date', 'hour_str'])['stop_count'].sum().reset_index()
    final_transit_counts.rename(columns={'hour_str': 'Hour', 'date': 'Date', 'stop_count': 'Transit_Count'}, inplace=True)

    return final_transit_counts

def integrate_data(transit_df):
    weather_path = os.path.join(PROCESSED_DATA_DIR, 'weather_clean.csv')
    weather_df = pd.read_csv(weather_path)

    weather_df['DateTime'] = pd.to_datetime(weather_df['DateTime'])
    weather_df['Date'] = weather_df['DateTime'].dt.normalize()
    weather_df['Hour'] = weather_df['DateTime'].dt.hour

    integrated_df = pd.merge(weather_df, transit_df, on=['Date', 'Hour'], how='left')
    integrated_df['Transit_Count'] = integrated_df['Transit_Count'].fillna(0).astype(int)

    # Filter to only include the date range where transit data is available
    min_transit_date = transit_df['Date'].min()
    max_transit_date = transit_df['Date'].max()
    
    print(f"Filtering dataset to valid transit data range: {min_transit_date.date()} to {max_transit_date.date()}")
    integrated_df = integrated_df[(integrated_df['Date'] >= min_transit_date) & (integrated_df['Date'] <= max_transit_date)]

    return integrated_df

def main():
    if not os.path.exists(FINAL_DATA_DIR):
        os.makedirs(FINAL_DATA_DIR)

    stop_times, trips, calendar_dates = load_gtfs()
    transit_counts = process_transit_data(stop_times, trips, calendar_dates)

    final_df = integrate_data(transit_counts)

    output_path = os.path.join(FINAL_DATA_DIR, 'integrated_dataset.csv')
    final_df.to_csv(output_path, index=False)
    print(f"Integrated dataset saved at {output_path}")

    print(final_df.describe())

if __name__ == "__main__":
    main()
