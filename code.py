import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np


def load_epw_wind_data(epw_path: str | Path) -> Tuple[List[Dict[str, float]], Optional[int]]:
    """Read an EPW file and return wind observations and the year found in the data."""
    path = Path(epw_path)
    if not path.exists():
        raise FileNotFoundError(f"EPW file not found: {path}")

    rows: List[Dict[str, float]] = []
    found_year: Optional[int] = None

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        # Skip the first 8 header lines of the EPW file
        for _ in range(8):
            next(reader, None)

        for values in reader:
            if not values or len(values) < 22:
                continue

            try:
                # Extract year from the first column if not already found
                if found_year is None and values[0]:
                    found_year = int(values[0])

                direction = float(values[20])
                speed = float(values[21])
                if not math.isnan(direction) and not math.isnan(speed):
                    rows.append({"direction": direction, "speed": speed})
            except (ValueError, IndexError):
                continue

    return rows, found_year


def sector_for_direction(direction: float, sectors: int = 16) -> int:
    """Map a compass direction to a wind rose sector index."""
    if sectors <= 0:
        raise ValueError("sectors must be a positive integer")

    normalized = (direction % 360.0 + (360.0 / (2 * sectors))) % 360.0
    sector = int(normalized / (360.0 / sectors))
    return sector % sectors


def summarize_by_direction(
    wind_data: Sequence[Dict[str, float]],
    sectors: int = 16,
) -> Dict[str, Any]:
    """Create a simple sector summary of counts and mean speeds."""
    counts = [0.0 for _ in range(sectors)]
    speed_totals = [0.0 for _ in range(sectors)]
    speed_counts = [0 for _ in range(sectors)]

    for entry in wind_data:
        sector = sector_for_direction(float(entry["direction"]), sectors=sectors)
        counts[sector] += 1.0
        speed_totals[sector] += float(entry["speed"])
        speed_counts[sector] += 1

    mean_speeds = []
    for index in range(sectors):
        if speed_counts[index]:
            mean_speeds.append(speed_totals[index] / speed_counts[index])
        else:
            mean_speeds.append(0.0)

    labels = []
    for sector in range(sectors):
        angle = sector * (360.0 / sectors)
        labels.append(_sector_label(angle))

    return {
        "counts": counts,
        "mean_speeds": mean_speeds,
        "sector_labels": labels,
        "sectors": sectors,
    }


def _sector_label(angle: float) -> str:
    compass_points = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    index = int((angle / 22.5) + 0.5) % 16
    return compass_points[index]


def build_wind_rose_plot(
    wind_data: Sequence[Dict[str, float]],
    output_path: str | Path,
    sectors: int = 16,
    speed_bins: Optional[Sequence[float]] = None,
    year: Optional[int] = None,
) -> Path:
    """Create a polar wind rose plot and save it to disk."""
    if not wind_data:
        raise ValueError("No wind data available to plot")

    if speed_bins is None:
        # Dynamically calculate range based on max speed in file
        max_v = max((entry["speed"] for entry in wind_data), default=10.0)
        upper_limit = math.ceil(max_v) if max_v > 0 else 10.0
        speed_bins = np.linspace(0, upper_limit, 7).tolist()

    speed_bins = [float(value) for value in speed_bins]

    if len(speed_bins) < 2:
        raise ValueError("speed_bins must contain at least two values")

    summary = summarize_by_direction(wind_data, sectors=sectors)
    angles = np.linspace(0, 2 * np.pi, sectors, endpoint=False)
    width = 2 * np.pi / sectors
    total_observations = len(wind_data)

    counts_by_bin = [[0.0 for _ in range(sectors)] for _ in range(len(speed_bins) - 1)]
    for entry in wind_data:
        sector = sector_for_direction(float(entry["direction"]), sectors=sectors)
        speed = float(entry["speed"])
        bin_index = _speed_bin_index(speed, speed_bins)
        counts_by_bin[bin_index][sector] += 1.0

    # Convert raw counts to percentage frequency
    stacked_counts = (np.array(counts_by_bin) / total_observations) * 100
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(8, 8))
    # Use jet colormap for vibrant, high-contrast colors (Blue -> Cyan -> Yellow -> Red)
    colors = plt.cm.jet(np.linspace(0, 1, len(speed_bins) - 1))

    max_radius = np.max(np.sum(stacked_counts, axis=0)) if stacked_counts.size > 0 else 1.0
    if max_radius <= 0:
        max_radius = 1.0

    cumulative_bottom = np.zeros(sectors)
    for index, values in enumerate(stacked_counts):
        if not any(values):
            continue
        ax.bar(
            angles,
            values,
            width=width * 0.8, # Added gaps between sector bars
            bottom=cumulative_bottom, # Stack bars correctly
            color=colors[index],
            alpha=1.0, # Full brightness for colors
            edgecolor="black", # Segment outlines for clarity
            linewidth=0.5,
            label=f"{speed_bins[index]:.1f} - {speed_bins[index + 1]:.1f} m/s",
        )
        cumulative_bottom += values

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(summary["sector_labels"])
    
    # Set radial axis to show percentage
    ax.set_ylim(0, max_radius * 1.1)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_rlabel_position(22.5)  # Offset radial labels to avoid bar overlap
    
    title = f"Wind Rose for Year {year}" if year else "Wind Rose"
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(title="wind velocity in m/s", loc="upper right", bbox_to_anchor=(1.3, 1.1))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def _speed_bin_index(speed: float, speed_bins: Sequence[float]) -> int:
    for index in range(len(speed_bins) - 1):
        if speed_bins[index] <= speed < speed_bins[index + 1]:
            return index
    return len(speed_bins) - 2


def main() -> None:
    input_dir = Path("epw-files")
    output_dir = Path("output_wind_roses")

    if not input_dir.is_dir():
        print(f"Error: Directory '{input_dir}' not found.")
        return

    output_dir.mkdir(exist_ok=True)
    epw_files = list(input_dir.glob("*.epw"))

    if not epw_files:
        print(f"No EPW files found in {input_dir}")
        return

    print(f"Processing {len(epw_files)} files...")

    for epw_path in epw_files:
        try:
            wind_data, year = load_epw_wind_data(epw_path)
            if not wind_data:
                print(f"Skipping {epw_path.name}: No valid data.")
                continue

            output_filename = output_dir / f"{epw_path.stem}.png"
            build_wind_rose_plot(wind_data, output_path=output_filename, year=year)
            print(f"Generated: {output_filename.name}")
        except Exception as e:
            print(f"Error processing {epw_path.name}: {e}")


if __name__ == "__main__":
    main()
