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

    # -------------------------
    # LAP DATA
    # -------------------------

    laps = race.laps

    print("Lap data collected!")

    laps_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "laps"
    laps_dir.mkdir(parents=True, exist_ok=True)

    laps_file = laps_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    laps.to_csv(laps_file, index=False)

    print(f"Lap data saved to {laps_file}")


    # -------------------------
    # STINT DATA
    # -------------------------

    stints = (
        laps
        .groupby(["Driver", "Stint", "Compound"], dropna=False)
        .agg(
            StartLap=("LapNumber", "min"),
            EndLap=("LapNumber", "max"),
            StintLaps=("LapNumber", "count"),
            AverageLapTime=("LapTime", "mean"),
            FastestLapTime=("LapTime", "min"),
            AverageTyreLife=("TyreLife", "mean")
        )
        .reset_index()
    )

    print("Stint data created!")

    stints_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "stints"
    stints_dir.mkdir(parents=True, exist_ok=True)

    stints_file = stints_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    stints.to_csv(stints_file, index=False)

    # -------------------------
    # PIT STOP DATA
    # -------------------------

    pit_stops = laps[
        laps["PitInTime"].notna()
    ][
        ["Driver", "LapNumber", "PitInTime", "PitOutTime"]
    ].copy()

    print("Pit stop data collected!")

    pit_stops_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "pit_stops"
    pit_stops_dir.mkdir(parents=True, exist_ok=True)

    pit_stops_file = pit_stops_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    pit_stops.to_csv(pit_stops_file, index=False)

    # -------------------------
    # WEATHER DATA
    # -------------------------

    weather = race.weather_data

    print("Weather data collected!")

    weather_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "weather"
    weather_dir.mkdir(parents=True, exist_ok=True)

    weather_file = weather_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    weather.to_csv(weather_file, index=False)


if __name__ == "__main__":
    collect_race_data(2025, "British")