import fastf1
import pandas as pd
from pathlib import Path
import time

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "fastf1_cache"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)

def save_if_not_exists(df, output_file, dataset_name):
    if output_file.exists():
        try:
            existing_df = pd.read_csv(output_file)

            if len(existing_df) > 0:
                print(f"{dataset_name} already exists. Skipping.")
                return

            print(f"{dataset_name} exists but is empty. Replacing it.")

        except Exception:
            print(f"{dataset_name} could not be read. Replacing it.")

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

    base_dir = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "raw"
    )

    for folder in folders:
        file_path = base_dir / folder / filename

        if not file_path.exists():
            return False

        try:
            df = pd.read_csv(file_path)

            if len(df) == 0:
                return False

        except Exception:
            return False

    return True
def collect_race_data(year, round_number, event):

    if race_data_exists(year, event):
        print(f"All data already exists for {year} {event}. Skipping.")
        return

    print(f"Collecting data for {year} {event}")

    # -------------------------
    # RACE SESSION
    # -------------------------

    race = fastf1.get_session(year, round_number, "R")

    try:
        race.load(
            laps=True,
            telemetry=False,
            weather=True
        )
        print("Race session loaded successfully!")

    except Exception as e:
        print(f"ERROR: Race session could not be loaded for {year} {event}")
        print(f"Reason: {e}")
        race = None

    # -------------------------
    # RACE RESULTS
    # -------------------------

    if race is not None:

        try:
            race_results = race.results

            output_dir = (
                Path(__file__).resolve().parent.parent
                / "data" / "raw" / "race_results"
            )

            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = (
                output_dir
                / f"{year}_{event.lower().replace(' ', '_')}.csv"
            )

            save_if_not_exists(
                race_results,
                output_file,
                "Race results"
            )

        except Exception as e:
            print(f"ERROR: Could not collect race results for {year} {event}")
            print(f"Reason: {e}")

    # -------------------------
    # QUALIFYING DATA
    # -------------------------

    qualifying = fastf1.get_session(year, round_number, "Q")

    try:
        qualifying.load(
            laps=False,
            telemetry=False,
            weather=False
        )
        print("Qualifying session loaded successfully!")

        qualifying_results = qualifying.results

        qualifying_dir = (
            Path(__file__).resolve().parent.parent
            / "data" / "raw" / "qualifying"
        )

        qualifying_dir.mkdir(parents=True, exist_ok=True)

        qualifying_file = (
            qualifying_dir
            / f"{year}_{event.lower().replace(' ', '_')}.csv"
        )

        save_if_not_exists(
            qualifying_results,
            qualifying_file,
            "Qualifying results"
        )

    except Exception as e:
        print(f"ERROR: Could not collect qualifying for {year} {event}")
        print(f"Reason: {e}")

    # -------------------------
    # LAP DATA
    # -------------------------

    laps = None

    if race is not None:

        try:
            laps = race.laps
            print("Lap data collected!")

            laps_dir = (
                Path(__file__).resolve().parent.parent
                / "data" / "raw" / "laps"
            )

            laps_dir.mkdir(parents=True, exist_ok=True)

            laps_file = (
                laps_dir
                / f"{year}_{event.lower().replace(' ', '_')}.csv"
            )

            save_if_not_exists(
                laps,
                laps_file,
                "Lap data"
            )

        except Exception as e:
            print(f"ERROR: Lap data could not be accessed for {year} {event}")
            print(f"Reason: {e}")

    # -------------------------
    # STINT DATA
    # -------------------------

    if laps is not None:

        try:
            stints = (
                laps
                .groupby(
                    ["Driver", "Stint", "Compound"],
                    dropna=False
                )
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

            stints_dir = (
                Path(__file__).resolve().parent.parent
                / "data" / "raw" / "stints"
            )

            stints_dir.mkdir(parents=True, exist_ok=True)

            stints_file = (
                stints_dir
                / f"{year}_{event.lower().replace(' ', '_')}.csv"
            )

            save_if_not_exists(
                stints,
                stints_file,
                "Stint data"
            )

        except Exception as e:
            print(f"ERROR: Could not create stint data for {year} {event}")
            print(f"Reason: {e}")

    # -------------------------
    # PIT STOP DATA
    # -------------------------

    if laps is not None:

        try:
            pit_stops = laps[
                laps["PitInTime"].notna()
            ][
                ["Driver", "LapNumber", "PitInTime", "PitOutTime"]
            ].copy()

            print("Pit stop data collected!")

            pit_stops_dir = (
                Path(__file__).resolve().parent.parent
                / "data" / "raw" / "pit_stops"
            )

            pit_stops_dir.mkdir(parents=True, exist_ok=True)

            pit_stops_file = (
                pit_stops_dir
                / f"{year}_{event.lower().replace(' ', '_')}.csv"
            )

            save_if_not_exists(
                pit_stops,
                pit_stops_file,
                "Pit stop data"
            )

        except Exception as e:
            print(f"ERROR: Could not create pit stop data for {year} {event}")
            print(f"Reason: {e}")

    # -------------------------
    # WEATHER DATA
    # -------------------------

    if race is not None:

        try:
            weather = race.weather_data
            print("Weather data collected!")

            weather_dir = (
                Path(__file__).resolve().parent.parent
                / "data" / "raw" / "weather"
            )

            weather_dir.mkdir(parents=True, exist_ok=True)

            weather_file = (
                weather_dir
                / f"{year}_{event.lower().replace(' ', '_')}.csv"
            )

            save_if_not_exists(
                weather,
                weather_file,
                "Weather data"
            )

        except Exception as e:
            print(f"ERROR: Could not collect weather for {year} {event}")
            print(f"Reason: {e}")

if __name__ == "__main__":

    for year in range(2020, 2026):

        print("\n" + "=" * 60)
        print(f"STARTING SEASON {year}")
        print("=" * 60)

        schedule = None

        for attempt in range(1, 4):
            try:
                print(
                    f"Loading {year} schedule "
                    f"(attempt {attempt}/3)..."
                )

                schedule = fastf1.get_event_schedule(year)
                schedule = schedule[
                    schedule["RoundNumber"] > 0
                ]

                print(f"{year} schedule loaded successfully!")
                break

            except Exception as e:
                print(
                    f"Schedule attempt {attempt} "
                    f"failed for {year}."
                )
                print(f"Reason: {e}")

                time.sleep(10)

        if schedule is None:
            print(
                f"ERROR: Could not load schedule "
                f"for {year} after 3 attempts."
            )
            continue

        for _, event in schedule.iterrows():

            try:
                collect_race_data(
                    year,
                    event["RoundNumber"],
                    event["EventName"]
                )

            except Exception as e:
                print(
                    f"ERROR: Could not collect "
                    f"{event['EventName']} {year}"
                )
                print(f"Reason: {e}")

            time.sleep(5)