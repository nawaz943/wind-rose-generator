# Wind Rose Generator

A Python utility to parse EnergyPlus Weather (EPW) files and generate visual wind rose plots using Matplotlib and Numpy.

## Features
- Parses wind speed and direction from EPW files.
- Categorizes wind data into 16 compass sectors.
- Generates high-resolution polar plots (PNG) with customizable speed bins.
- Batch processes multiple files in a directory.

## Installation

```bash
pip install -r requirements.txt
```

## Usage
1. Place your `.epw` files in a folder named `epw-files/`.
2. Run the generator:
   ```bash
   python code.py --input epw-files/ --output output_wind_roses/
   ```
   You can customize the input and output directories using the `--input` and `--output` flags.
   For example: `python code.py -i my_epw_data/ -o my_wind_rose_plots/`
3. Find your generated plots in the `output_wind_roses/` directory.