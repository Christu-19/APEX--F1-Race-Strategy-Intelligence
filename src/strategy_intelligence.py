import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

PROCESSED_DATA_DIR = (
    PROJECT_DIR / "data" / "processed" / "strategy"
)

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# RACE ORDER
# Used to create a chronological Round number.
# ============================================================

RACE_ORDER = {
    2020: [
        "austrian grand prix",
        "styrian grand prix",
        "hungarian grand prix",
        "british grand prix",
        "70th anniversary grand prix",
        "spanish grand prix",
        "belgian grand prix",
        "italian grand prix",
        "tuscan grand prix",
        "russian grand prix",
        "eifel grand prix",
        "portuguese grand prix",
        "emilia romagna grand prix",
        "turkish grand prix",
        "bahrain grand prix",
        "sakhir grand prix",
        "abu dhabi grand prix"
    ],

    2021: [
        "bahrain grand prix",
        "emilia romagna grand prix",
        "portuguese grand prix",
        "spanish grand prix",
        "monaco grand prix",
        "azerbaijan grand prix",
        "french grand prix",
        "styrian grand prix",
        "austrian grand prix",
        "british grand prix",
        "hungarian grand prix",
        "belgian grand prix",
        "dutch grand prix",
        "italian grand prix",
        "russian grand prix",
        "turkish grand prix",
        "united states grand prix",
        "mexico city grand prix",
        "são paulo grand prix",
        "qatar grand prix",
        "saudi arabian grand prix",
        "abu dhabi grand prix"
    ],

    2022: [
        "bahrain grand prix",
        "saudi arabian grand prix",
        "australian grand prix",
        "emilia romagna grand prix",
        "miami grand prix",
        "spanish grand prix",
        "monaco grand prix",
        "azerbaijan grand prix",
        "canadian grand prix",
        "british grand prix",
        "austrian grand prix",
        "french grand prix",
        "hungarian grand prix",
        "belgian grand prix",
        "dutch grand prix",
        "italian grand prix",
        "singapore grand prix",
        "japanese grand prix",
        "united states grand prix",
        "mexico city grand prix",
        "são paulo grand prix",
        "abu dhabi grand prix"
    ],

    2023: [
        "bahrain grand prix",
        "saudi arabian grand prix",
        "australian grand prix",
        "azerbaijan grand prix",
        "miami grand prix",
        "monaco grand prix",
        "spanish grand prix",
        "canadian grand prix",
        "austrian grand prix",
        "british grand prix",
        "hungarian grand prix",
        "belgian grand prix",
        "dutch grand prix",
        "italian grand prix",
        "singapore grand prix",
        "japanese grand prix",
        "qatar grand prix",
        "united states grand prix",
        "mexico city grand prix",
        "são paulo grand prix",
        "las vegas grand prix",
        "abu dhabi grand prix"
    ],

    2024: [
        "bahrain grand prix",
        "saudi arabian grand prix",
        "australian grand prix",
        "japanese grand prix",
        "chinese grand prix",
        "miami grand prix",
        "emilia romagna grand prix",
        "monaco grand prix",
        "canadian grand prix",
        "spanish grand prix",
        "austrian grand prix",
        "british grand prix",
        "hungarian grand prix",
        "belgian grand prix",
        "dutch grand prix",
        "italian grand prix",
        "azerbaijan grand prix",
        "singapore grand prix",
        "united states grand prix",
        "mexico city grand prix",
        "são paulo grand prix",
        "las vegas grand prix",
        "qatar grand prix",
        "abu dhabi grand prix"
    ],

    2025: [
        "australian grand prix",
        "chinese grand prix",
        "japanese grand prix",
        "bahrain grand prix",
        "saudi arabian grand prix",
        "miami grand prix",
        "emilia romagna grand prix",
        "monaco grand prix",
        "spanish grand prix",
        "canadian grand prix",
        "austrian grand prix",
        "british grand prix",
        "belgian grand prix",
        "hungarian grand prix",
        "dutch grand prix",
        "italian grand prix",
        "azerbaijan grand prix",
        "singapore grand prix",
        "united states grand prix",
        "mexico city grand prix",
        "são paulo grand prix",
        "las vegas grand prix",
        "qatar grand prix",
        "abu dhabi grand prix"
    ]
}


# ============================================================
# LOAD ONE RACE
# ============================================================

def load_race_data(laps_file, race_results_file):

    laps = pd.read_csv(laps_file)

    race_results = pd.read_csv(
        race_results_file
    )

    return laps, race_results


# ============================================================
# STINT SUMMARY
# ============================================================

def create_stint_summary(laps):

    laps = laps.copy()

    laps["LapTime"] = pd.to_timedelta(
        laps["LapTime"],
        errors="coerce"
    ).dt.total_seconds()

    stint_summary = (
        laps
        .groupby(
            [
                "Driver",
                "Stint",
                "Compound"
            ],
            as_index=False
        )
        .agg(
            StartLap=("LapNumber", "min"),
            EndLap=("LapNumber", "max"),
            LapsCompleted=("LapNumber", "count"),
            AverageLapTime=("LapTime", "mean"),
            MinLapTime=("LapTime", "min"),
            MaxTyreLife=("TyreLife", "max")
        )
    )

    return stint_summary


# ============================================================
# DRIVER STRATEGY
# ============================================================

def create_driver_strategies(stint_summary):

    driver_strategies = (
        stint_summary
        .sort_values(
            [
                "Driver",
                "Stint"
            ]
        )
        .groupby("Driver")
        .agg(
            NumberOfStints=(
                "Stint",
                "nunique"
            ),

            CompoundsUsed=(
                "Compound",
                lambda x: " → ".join(
                    x.astype(str)
                )
            ),

            TotalLaps=(
                "LapsCompleted",
                "sum"
            )
        )
        .reset_index()
    )

    return driver_strategies


# ============================================================
# PIT STOP SUMMARY
# ============================================================

def create_pit_stop_summary(laps):

    pit_stop_summary = (
        laps
        .groupby("Driver")
        .agg(
            PitStops=(
                "PitInTime",
                "count"
            ),

            TotalStints=(
                "Stint",
                "nunique"
            )
        )
        .reset_index()
    )

    return pit_stop_summary


# ============================================================
# STRATEGY PROFILE
# ============================================================

def create_strategy_profile(
    driver_strategies,
    pit_stop_summary,
    race_results
):

    strategy_profile = driver_strategies.merge(
        pit_stop_summary[
            [
                "Driver",
                "PitStops"
            ]
        ],
        on="Driver",
        how="left"
    )

    strategy_profile = strategy_profile.merge(
        race_results[
            [
                "Abbreviation",
                "Position",
                "TeamName"
            ]
        ],
        left_on="Driver",
        right_on="Abbreviation",
        how="left"
    )

    strategy_profile = strategy_profile[
        [
            "Driver",
            "TeamName",
            "Position",
            "TotalLaps",
            "NumberOfStints",
            "PitStops",
            "CompoundsUsed"
        ]
    ]

    return strategy_profile


# ============================================================
# TYRE AGE VS PACE
# ============================================================

def create_tyre_age_pace(laps):

    tyre_age_pace = (
        laps[
            [
                "Compound",
                "TyreLife",
                "LapTime"
            ]
        ]
        .dropna(
            subset=[
                "Compound",
                "TyreLife",
                "LapTime"
            ]
        )
        .copy()
    )

    tyre_age_pace["LapTime"] = pd.to_timedelta(
        tyre_age_pace["LapTime"],
        errors="coerce"
    ).dt.total_seconds()

    tyre_age_pace = tyre_age_pace.dropna(
        subset=["LapTime"]
    )

    tyre_age_pace = (
        tyre_age_pace
        .groupby(
            [
                "Compound",
                "TyreLife"
            ],
            as_index=False
        )
        .agg(
            AverageLapTime=(
                "LapTime",
                "mean"
            ),

            NumberOfLaps=(
                "LapTime",
                "count"
            )
        )
    )

    return tyre_age_pace


# ============================================================
# RACE PHASE PACE
# ============================================================

def create_phase_pace(laps):

    laps = laps.copy()

    laps["LapTime"] = pd.to_timedelta(
        laps["LapTime"],
        errors="coerce"
    ).dt.total_seconds()

    # Use the maximum race lap in the dataset.
    # This prevents assuming every race has exactly 52 laps.
    max_lap = laps["LapNumber"].max()

    bins = [
        0,
        max_lap * 0.2,
        max_lap * 0.4,
        max_lap * 0.6,
        max_lap * 0.8,
        max_lap
    ]

    labels = [
        "Early Race",
        "Early-Mid Race",
        "Mid Race",
        "Late-Mid Race",
        "Late Race"
    ]

    laps["RacePhase"] = pd.cut(
        laps["LapNumber"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    phase_pace = (
        laps[
            [
                "RacePhase",
                "Compound",
                "LapTime"
            ]
        ]
        .dropna(
            subset=[
                "RacePhase",
                "Compound",
                "LapTime"
            ]
        )
        .groupby(
            [
                "RacePhase",
                "Compound"
            ],
            as_index=False,
            observed=True
        )
        .agg(
            AverageLapTime=(
                "LapTime",
                "mean"
            ),

            NumberOfLaps=(
                "LapTime",
                "count"
            )
        )
    )

    return phase_pace


# ============================================================
# ADD RACE METADATA
# ============================================================

def add_race_metadata(
    df,
    year,
    race_name,
    round_number
):

    df = df.copy()

    df["Year"] = year

    df["Race"] = race_name

    df["Round"] = round_number

    return df


# ============================================================
# PROCESS ONE RACE
# ============================================================

def process_one_race(
    laps_file,
    race_results_file,
    year,
    race_name,
    round_number
):

    print(
        f"\nProcessing {year} - {race_name}"
    )

    laps, race_results = load_race_data(
        laps_file,
        race_results_file
    )

    # -------------------------------
    # Stint analysis
    # -------------------------------

    stint_summary = create_stint_summary(
        laps
    )

    driver_strategies = (
        create_driver_strategies(
            stint_summary
        )
    )

    # -------------------------------
    # Pit stops
    # -------------------------------

    pit_stop_summary = (
        create_pit_stop_summary(
            laps
        )
    )

    # -------------------------------
    # Strategy profile
    # -------------------------------

    strategy_profile = (
        create_strategy_profile(
            driver_strategies,
            pit_stop_summary,
            race_results
        )
    )

    # -------------------------------
    # Tyre age
    # -------------------------------

    tyre_age_pace = (
        create_tyre_age_pace(
            laps
        )
    )

    # -------------------------------
    # Race phase
    # -------------------------------

    phase_pace = (
        create_phase_pace(
            laps
        )
    )

    # -------------------------------
    # Add metadata
    # -------------------------------

    stint_summary = add_race_metadata(
        stint_summary,
        year,
        race_name,
        round_number
    )

    strategy_profile = add_race_metadata(
        strategy_profile,
        year,
        race_name,
        round_number
    )

    tyre_age_pace = add_race_metadata(
        tyre_age_pace,
        year,
        race_name,
        round_number
    )

    phase_pace = add_race_metadata(
        phase_pace,
        year,
        race_name,
        round_number
    )

    return (
        stint_summary,
        strategy_profile,
        tyre_age_pace,
        phase_pace
    )


# ============================================================
# FIND ALL RACES
# ============================================================

def find_all_races():

    laps_folder = (
        RAW_DATA_DIR / "laps"
    )

    race_results_folder = (
        RAW_DATA_DIR / "race_results"
    )

    laps_files = sorted(
        laps_folder.glob(
            "*_grand_prix.csv"
        )
    )

    race_files = sorted(
        race_results_folder.glob(
            "*_grand_prix.csv"
        )
    )

    race_results_lookup = {
        file.name: file
        for file in race_files
    }

    races = []

    for laps_file in laps_files:

        race_results_file = (
            race_results_lookup.get(
                laps_file.name
            )
        )

        if race_results_file is None:

            print(
                f"Skipping {laps_file.name}: "
                "race-results file missing."
            )

            continue

        try:

            year = int(
                laps_file.name[:4]
            )

        except ValueError:

            print(
                f"Skipping invalid filename: "
                f"{laps_file.name}"
            )

            continue

        race_name = (
            laps_file
            .stem[5:]
            .replace("_", " ")
        )

        race_name = race_name.replace(
            "grand prix",
            "Grand Prix"
        )

        race_name = race_name.title()

        race_key = (
            race_name.lower()
        )

        if (
            year in RACE_ORDER
            and race_key in RACE_ORDER[year]
        ):

            round_number = (
                RACE_ORDER[year]
                .index(race_key)
                + 1
            )

        else:

            round_number = None

        races.append(
            {
                "laps_file": laps_file,
                "race_results_file": race_results_file,
                "year": year,
                "race_name": race_name,
                "round": round_number
            }
        )

    races = sorted(
        races,
        key=lambda x: (
            x["year"],
            x["round"]
            if x["round"] is not None
            else 999
        )
    )

    return races


# ============================================================
# PROCESS ALL RACES
# ============================================================

def process_all_races():

    races = find_all_races()

    print(
        f"\nFound {len(races)} race datasets."
    )

    all_stints = []
    all_strategy_profiles = []
    all_tyre_age_pace = []
    all_phase_pace = []

    successful_races = 0
    failed_races = []

    for race in races:

        try:

            (
                stint_summary,
                strategy_profile,
                tyre_age_pace,
                phase_pace
            ) = process_one_race(
                race["laps_file"],
                race["race_results_file"],
                race["year"],
                race["race_name"],
                race["round"]
            )

            all_stints.append(
                stint_summary
            )

            all_strategy_profiles.append(
                strategy_profile
            )

            all_tyre_age_pace.append(
                tyre_age_pace
            )

            all_phase_pace.append(
                phase_pace
            )

            successful_races += 1

        except Exception as error:

            print(
                f"ERROR processing "
                f"{race['year']} "
                f"{race['race_name']}:"
            )

            print(error)

            failed_races.append(
                {
                    "Year": race["year"],
                    "Race": race["race_name"],
                    "Error": str(error)
                }
            )

    # ========================================================
    # COMBINE RESULTS
    # ========================================================

    if all_stints:

        combined_stints = pd.concat(
            all_stints,
            ignore_index=True
        )

        combined_stints.to_csv(
            PROCESSED_DATA_DIR
            / "all_stints.csv",
            index=False
        )

    if all_strategy_profiles:

        combined_strategy_profiles = pd.concat(
            all_strategy_profiles,
            ignore_index=True
        )

        combined_strategy_profiles.to_csv(
            PROCESSED_DATA_DIR
            / "all_strategy_profiles.csv",
            index=False
        )

    if all_tyre_age_pace:

        combined_tyre_age_pace = pd.concat(
            all_tyre_age_pace,
            ignore_index=True
        )

        combined_tyre_age_pace.to_csv(
            PROCESSED_DATA_DIR
            / "all_tyre_age_pace.csv",
            index=False
        )

    if all_phase_pace:

        combined_phase_pace = pd.concat(
            all_phase_pace,
            ignore_index=True
        )

        combined_phase_pace.to_csv(
            PROCESSED_DATA_DIR
            / "all_phase_pace.csv",
            index=False
        )

    # ========================================================
    # SAVE ERROR LOG
    # ========================================================

    if failed_races:

        failed_df = pd.DataFrame(
            failed_races
        )

        failed_df.to_csv(
            PROCESSED_DATA_DIR
            / "strategy_processing_errors.csv",
            index=False
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n" + "=" * 60)
    print("STRATEGY PIPELINE COMPLETE")
    print("=" * 60)

    print(
        f"Races found: {len(races)}"
    )

    print(
        f"Successfully processed: "
        f"{successful_races}"
    )

    print(
        f"Failed: {len(failed_races)}"
    )

    print(
        f"\nOutput directory:"
        f"\n{PROCESSED_DATA_DIR}"
    )

    if failed_races:

        print(
            "\nFailed races:"
        )

        for race in failed_races:

            print(
                f"- {race['Year']} "
                f"{race['Race']}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    process_all_races()