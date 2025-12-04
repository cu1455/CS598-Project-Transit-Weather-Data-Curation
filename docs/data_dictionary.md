# Data Dictionary: Integrated Transit and Weather Dataset

## Overview
This dataset integrates hourly public transit activity counts from Grand River Transit (GRT) with historical weather data from Environment and Climate Change Canada (ECCC) for the Waterloo Region.

## Content

| Column Name | Data Type | Description | Source |
| :--- | :--- | :--- | :--- |
| `DateTime` | String (ISO 8601) | The specific date and hour of the observation (e.g., `2024-01-01 08:00:00`). | Generated |
| `Year` | Integer | The year of the observation. | Derived from DateTime |
| `Month` | Integer | The month of the observation (1-12). | Derived from DateTime |
| `Day` | Integer | The day of the month (1-31). | Derived from DateTime |
| `Time (LST)` | String | Local Standard Time of the weather observation (HH:MM). | ECCC |
| `Temp (°C)` | Float | Air temperature in degrees Celsius. Missing values have been linearly interpolated. | ECCC |
| `Precip. Amount (mm)` | Float | Total precipitation in millimeters. Missing values have been imputed with 0. | ECCC |
| `Date` | String (YYYY-MM-DD) | The date component, useful for daily aggregation. | Derived |
| `Hour` | Integer | The hour component (0-23). | Derived |
| `Transit_Count` | Integer | **Target Variable**. The total number of scheduled transit stop events across the entire GRT network for this hour. Represents transit service availability/activity. | GRT (Aggregated) |
