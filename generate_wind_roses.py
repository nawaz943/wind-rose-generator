"""
Wind rose generator from EPW weather files.

- Reads every *.epw file in the ./input_files folder.
- Builds a wind rose using a CFD-contour-style colour range (jet colormap).
- Saves each chart to ./output_files as "Wind rose <year>.png",
  where <year> is taken from the hourly data rows of the EPW file.
"""

import os
import glob

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # non-interactive backend; we only save files
import matplotlib.pyplot as plt
from matplotlib import cm
from windrose import WindroseAxes

# --- Configuration ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input_files")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_files")

# EPW format: 8 header lines, then comma-separated hourly data rows.
HEADER_LINES = 8
COL_YEAR = 0          # field 1  -> year
COL_WIND_DIR = 20     # field 21 -> wind direction (degrees)
COL_WIND_SPD = 21     # field 22 -> wind speed (m/s)

NUM_SPEED_BINS = 8    # number of speed bands (more bands = smoother CFD gradient)
DPI = 200


def read_epw(path):
    """Return (year, wind_direction, wind_speed) from an EPW file."""
    df = pd.read_csv(path, skiprows=HEADER_LINES, header=None)

    years = df[COL_YEAR].astype(int)
    wind_dir = df[COL_WIND_DIR].astype(float)
    wind_spd = df[COL_WIND_SPD].astype(float)

    # Drop EPW missing values: wind speed 999, direction 999/>360.
    valid = (wind_spd < 999) & (wind_dir >= 0) & (wind_dir <= 360)
    wind_dir = wind_dir[valid]
    wind_spd = wind_spd[valid]

    # Most frequent year (robust for both single-year and mixed-year TMY files).
    year = int(years.mode().iloc[0])
    return year, wind_dir.to_numpy(), wind_spd.to_numpy()


def make_wind_rose(year, wind_dir, wind_spd, out_path):
    """Draw and save a single wind rose chart."""
    fig = plt.figure(figsize=(9, 9))
    ax = WindroseAxes.from_ax(fig=fig)

    # Speed bins spanning the data range, coloured with the CFD-style jet map.
    max_spd = float(np.ceil(wind_spd.max()))
    bins = np.linspace(0, max_spd, NUM_SPEED_BINS + 1)

    ax.bar(
        wind_dir,
        wind_spd,
        bins=bins,
        normed=True,          # show frequencies as percentages
        opening=0.9,
        edgecolor="white",
        linewidth=0.3,
        cmap=cm.jet,
    )

    ax.set_title(f"Wind Rose {year}", fontsize=18, fontweight="bold", pad=25)
    ax.set_legend(
        title="Wind speed (m/s)",
        loc="lower right",
        bbox_to_anchor=(1.1, -0.05),
        fontsize=9,
    )
    # Frequency rings labelled as percentages.
    ax.set_yticklabels([f"{t:.0f}%" for t in ax.get_yticks()])

    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    epw_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.epw")))
    if not epw_files:
        print(f"No .epw files found in: {INPUT_DIR}")
        print("Drop your EPW files there and run again.")
        return

    print(f"Found {len(epw_files)} EPW file(s) in {INPUT_DIR}\n")
    for path in epw_files:
        try:
            year, wind_dir, wind_spd = read_epw(path)
            out_path = os.path.join(OUTPUT_DIR, f"Wind rose {year}.png")
            make_wind_rose(year, wind_dir, wind_spd, out_path)
            print(f"  {os.path.basename(path)}  ->  {os.path.basename(out_path)}")
        except Exception as exc:
            print(f"  ERROR processing {os.path.basename(path)}: {exc}")

    print(f"\nDone. Wind roses saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
