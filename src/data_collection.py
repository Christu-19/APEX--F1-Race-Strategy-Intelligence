import fastf1
import pandas as pd
from pathlib import Path

def collect_race_data(year, event):
    print(f"Collecting data for {year} {event}")

    # RACE DATA

    race = fastf1.get_session(year, event, "R")
    race.load()

    print("Race session loaded successfully!")

    race_results = race.results

    output_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "race_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    race_results.to_csv(output_file, index=False)

    print(f"Race results saved to {output_file}")

    # QUALIFYING DATA

    qualifying = fastf1.get_session(year, event, "Q")
    qualifying.load()

    print("Qualifying session loaded successfully!")

    qualifying_results = qualifying.results

    qualifying_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "qualifying"
    qualifying_dir.mkdir(parents=True, exist_ok=True)

    qualifying_file = qualifying_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    qualifying_results.to_csv(qualifying_file, index=False)

    print(f"Qualifying results saved to {qualifying_file}")


if __name__ == "__main__":
    collect_race_data(2025, "British")