# AIM RaceTrack Lap Comparison Tool

A tool for visualizing and comparing laps on a race track using GPS data. This project includes code to plot GPS tracks over a race track image, providing animated comparisons of laps with detailed telemetry information.

## Features
- Load and process GPS data from CSV files
- Display an overhead race track image as the background
- Plot and animate multiple laps on the race track
- Zoom in on the track and follow the moving point
- Display real-time telemetry data such as speed and elapsed time

EXAMPLE: https://www.youtube.com/watch?v=hWge1PM26rc&t=3s

RESULT: https://www.youtube.com/shorts/0ms2u-YVogc

## How to Use
1. Upload your GPS data files in CSV format.
2. Adjust the race track image coordinates in the code to match your GPS data.
3. Run the script to visually compare the selected laps.

## Requirements
- Python 3.x
- Matplotlib
- Pandas
- Shapely
- PIL (Python Imaging Library)

## Installation
```bash
pip install matplotlib pandas shapely pillow

## Example usage
file_path_1 = 'path_to_your_first_csv_file.csv'
file_path_2 = 'path_to_your_second_csv_file.csv'

# Run the script with your data files
