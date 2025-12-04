import os
import requests
import zipfile
import io

# Config
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
GRT_GTFS_URL = "https://www.regionofwaterloo.ca/opendatadownloads/GRT_GTFS.zip"
# Station ID 48569 is WATERLOO INT'L A. Timeframe 1 is hourly.
WEATHER_URL_TEMPLATE = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=48569&Year={year}&Month={month}&Day=1&timeframe=1&submit=Download+Data"
YEARS = [2024, 2025]

def download_file(url, dest_path):
    # print(f"Downloading {url} to {dest_path}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(dest_path, 'wb') as f:
        f.write(response.content)

def download_weather_data(years, output_dir):
    for year in years:
        for month in range(1, 13):
            if year == 2025 and month > 11:
                continue

            url = WEATHER_URL_TEMPLATE.format(year=year, month=month)
            dest_path = os.path.join(output_dir, f"weather_waterloo_{year}_{month:02d}.csv")
            try:
                download_file(url, dest_path)
            except Exception as e:
                print(f"Failed to download weather data for {year}-{month}: {e}")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Download GRT GTFS
    gtfs_zip_path = os.path.join(DATA_DIR, "GRT_GTFS.zip")
    try:
        download_file(GRT_GTFS_URL, gtfs_zip_path)
        with zipfile.ZipFile(gtfs_zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(DATA_DIR, "gtfs"))
        print("GTFS data downloaded and extracted.")
    except Exception as e:
        print(f"Failed to download GRT GTFS data: {e}")

    # Download Weather Data
    print("Downloading weather data...")
    download_weather_data(YEARS, DATA_DIR)

if __name__ == "__main__":
    main()
