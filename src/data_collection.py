import fastf1
import pandas as pd
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "fastf1_cache"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)

def save_if_not_exists(df, output_file, dataset_name):
    if output_file.exists():
        print(f"{dataset_name} already exists. Skipping.")
    else:
        df.to_csv(output_file, index=False)
        print(f"{dataset_name} saved to {output_file}")

def race_data_exists(year, event):
    filename = f"{year}_{event.lower().replace(' ', '_')}.csv"

    folders = [
        "race_results",
        "qualifying",
        "laps",
        "stints",
        "pit_stops",
        "weather"
    ]

    base_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

    return all(
        (base_dir / folder / filename).exists()
        for folder in folders
    )

def collect_race_data(year, event):

    if race_data_exists(year, event):
        print(f"All data already exists for {year} {event}. Skipping.")
        return

    print(f"Collecting data for {year} {event}")

    # RACE DATA

    race = fastf1.get_session(year, event, "R")
    race.load()

    print("Race session loaded successfully!")

    race_results = race.results

    output_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "race_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    save_if_not_exists(
    race_results,
    output_file,
    "Race results"
    )

    # QUALIFYING DATA

    qualifying = fastf1.get_session(year, event, "Q")
    qualifying.load()

    print("Qualifying session loaded successfully!")

    qualifying_results = qualifying.results

    qualifying_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "qualifying"
    qualifying_dir.mkdir(parents=True, exist_ok=True)

    qualifying_file = qualifying_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    save_if_not_exists(
    qualifying_results,
    qualifying_file,
    "Qualifying results"
    )

    # -------------------------
    # LAP DATA
    # -------------------------

    laps = race.laps

    print("Lap data collected!")

    laps_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "laps"
    laps_dir.mkdir(parents=True, exist_ok=True)

    laps_file = laps_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    save_if_not_exists(
    laps,
    laps_file,
    "Lap data"
    )


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

    save_if_not_exists(
    stints,
    stints_file,
    "Stint data"
    )

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

    save_if_not_exists(
    pit_stops,
    pit_stops_file,
    "Pit stop data"
    )

    # -------------------------
    # WEATHER DATA
    # -------------------------

    weather = race.weather_data

    print("Weather data collected!")

    weather_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "weather"
    weather_dir.mkdir(parents=True, exist_ok=True)

    weather_file = weather_dir / f"{year}_{event.lower().replace(' ', '_')}.csv"

    save_if_not_exists(
    weather,
    weather_file,
    "Weather data"
    )


if __name__ == "__main__":
if __name__ == "__main__":

    for year in range(2020, 2026):

        print("\n" + "=" * 60)
        print(f"STARTING SEASON {year}")
        print("=" * 60)

        schedule = fastf1.get_event_schedule(year)

        schedule = schedule[schedule["RoundNumber"] > 0]

        for _, event in schedule.iterrows():

            try:
                collect_race_data(
                    year,
                    event["EventName"]
                )

            except Exception as e:
                print(f"ERROR: Could not collect {event['EventName']} {year}")
                print(f"Reason: {e}")