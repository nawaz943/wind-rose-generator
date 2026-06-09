import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("code.py")
SPEC = importlib.util.spec_from_file_location("wind_rose_module", MODULE_PATH)
assert SPEC and SPEC.loader
wind_rose_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wind_rose_module)

load_epw_wind_data = wind_rose_module.load_epw_wind_data
sector_for_direction = wind_rose_module.sector_for_direction
summarize_by_direction = wind_rose_module.summarize_by_direction


class WindRoseTests(unittest.TestCase):
    def test_load_epw_wind_data_parses_direction_and_speed(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".epw", delete=False) as handle:
            handle.write("Location,Test,Country,Region,Latitude,Longitude\n")
            handle.write("-\n")
            handle.write("-\n")
            handle.write("-\n")
            handle.write("-\n")
            handle.write("-\n")
            handle.write("-\n")
            handle.write("-\n")
            handle.write("2020,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,90,2.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n")
            handle.write("2020,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,180,4.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n")
            path = handle.name

        try:
            values, year = load_epw_wind_data(path)
            self.assertEqual(len(values), 2)
            self.assertEqual(values[0]["direction"], 90.0)
            self.assertEqual(values[0]["speed"], 2.5)
            self.assertEqual(values[1]["direction"], 180.0)
            self.assertEqual(values[1]["speed"], 4.0)
            self.assertEqual(year, 2020)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_sector_for_direction_and_summarize_by_direction(self) -> None:
        self.assertEqual(sector_for_direction(350, sectors=16), 0)
        self.assertEqual(sector_for_direction(10, sectors=16), 0)
        self.assertEqual(sector_for_direction(180, sectors=16), 8)

        summary = summarize_by_direction(
            [{"direction": 350, "speed": 5.0}, {"direction": 10, "speed": 2.0}, {"direction": 180, "speed": 1.0}],
            sectors=16,
        )
        self.assertEqual(summary["counts"][0], 2.0)
        self.assertEqual(summary["counts"][8], 1.0)


if __name__ == "__main__":
    unittest.main()
