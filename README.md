# EPW Wind Rose Generator

Generate wind rose charts from [EnergyPlus Weather (EPW)](https://energyplus.net/weather) files, styled with a CFD-contour-like colour range.

The script scans a folder of `.epw` files, plots a wind rose for each one using the hourly wind direction and wind speed records, and saves the charts as PNG images named after the year of the weather data.

## Features

- Batch-processes every `.epw` file in the input folder.
- Reads **wind direction** and **wind speed** directly from the EPW hourly data rows.
- Automatically filters out EPW missing values (e.g. wind speed flagged as `999`).
- Uses the **`jet`** colormap (blue → cyan → green → yellow → red) for a CFD contour look.
- Names each chart `Wind rose <year>.png`, where the year is read from the EPW data rows.

## Requirements

- Python 3.8+
- [`windrose`](https://pypi.org/project/windrose/)
- `matplotlib`
- `pandas`
- `numpy`

Install the dependencies with:

```bash
pip install windrose matplotlib pandas numpy
```

## Folder structure

```
wind-rose-gen-test/
├── generate_wind_roses.py
├── README.md
├── input_files/        # put your .epw files here
└── output_files/        # generated wind roses are saved here (created automatically)
```

## Usage

1. Place your `.epw` weather files inside the `input_files/` folder.
2. Run the script:

   ```bash
   python generate_wind_roses.py
   ```

3. Find the generated wind roses in the `output_files/` folder, named
   `Wind rose <year>.png` (for example, `Wind rose 2023.png`).

## How it works

EPW files contain 8 header lines followed by 8,760 hourly data rows. The script:

1. Skips the 8 header lines and reads the comma-separated data rows.
2. Extracts the **year** (column 1), **wind direction** (column 21), and
   **wind speed** (column 22).
3. Removes any rows with missing/invalid wind values.
4. Determines the chart year using the most frequent year in the data
   (robust for both single-year actual-year files and mixed-year TMY files).
5. Plots the wind rose with frequency rings shown as percentages and a
   wind-speed legend (m/s).

## Configuration

A few settings can be adjusted near the top of `generate_wind_roses.py`:

| Setting | Description | Default |
|---|---|---|
| `NUM_SPEED_BINS` | Number of wind-speed bands (more bands = smoother gradient) | `8` |
| `DPI` | Output image resolution | `200` |
| `INPUT_DIR` | Input folder for `.epw` files | `input_files` |
| `OUTPUT_DIR` | Output folder for charts | `output_files` |

## License

MIT
