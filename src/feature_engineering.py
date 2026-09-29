import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "data" / "processed"


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

# chronological race round
def add_race_round(df):

    df = df.copy()

    df["Round"] = df.apply(
        lambda row: RACE_ORDER[row["Year"]].index(row["Race"]) + 1,
        axis=1
    )

    return df

# load data
def load_data():

    race = pd.read_csv(
        PROCESSED_DATA_DIR / "cleaned_race_results.csv"
    )

    qualifying = pd.read_csv(
        PROCESSED_DATA_DIR / "cleaned_qualifying_results.csv"
    )

    return race, qualifying

# Merge dataset
def create_driver_race_dataset(race, qualifying):

    # Select qualifying features
    qualifying_features = qualifying[
        [
            "Year",
            "Race",
            "DriverId",
            "Position",
            "Q1",
            "Q2",
            "Q3"
        ]
    ].copy()

    # Rename qualifying position
    qualifying_features = qualifying_features.rename(
        columns={
            "Position": "QualifyingPosition"
        }
    )

    # Remove records without DriverId
    qualifying_features = qualifying_features.dropna(
        subset=["DriverId"]
    )

    # Merge race and qualifying data
    driver_race = race.merge(
        qualifying_features,
        on=["Year", "Race", "DriverId"],
        how="left",
        validate="one_to_one"
    )

    # Add chronological race round
    driver_race = add_race_round(driver_race)

    # Sort chronologically
    driver_race = driver_race.sort_values(
        ["Year", "Round"]
    ).copy()

    # Previous race finishing position
    driver_race["PreviousRaceFinish"] = (
        driver_race
        .groupby("DriverId")["Position"]
        .shift(1)
    )

    # Best qualifying lap time
    driver_race["BestQualifyingTime"] = driver_race[
        ["Q1", "Q2", "Q3"]
    ].min(axis=1)

     # Gap to the fastest qualifying time in each race
    pole_time = (
        driver_race
        .groupby(["Year", "Round"])["BestQualifyingTime"]
        .transform("min")
    )

    driver_race["QualifyingTimeGap"] = (
        driver_race["BestQualifyingTime"] - pole_time
    )

    # Historical average finishing position
    driver_race["DriverHistoricalAvgFinish"] = (
        driver_race
        .groupby("DriverId")["Position"]
        .transform(
            lambda x: x.shift(1).expanding().mean()
        )
    )

    # Average finishing position over the previous 3 races
    driver_race["DriverRecentForm"] = (
        driver_race
        .groupby("DriverId")["Position"]
        .transform(
            lambda x: x.shift(1).rolling(
                window=3,
                min_periods=1
            ).mean()
        )
    )

    # Calculate average finishing position for each team in each race
    team_race_performance = (
        driver_race
        .groupby(
            ["Year", "Round", "TeamId"],
            as_index=False
        )["Position"]
        .mean()
        .rename(
            columns={
                "Position": "TeamRaceAvgFinish"
            }
        )
    )

    # Sort team race history chronologically
    team_race_performance = team_race_performance.sort_values(
        ["TeamId", "Year", "Round"]
    ).copy()

    # Calculate historical team average before the current race
    team_race_performance["TeamHistoricalAvgFinish"] = (
        team_race_performance
        .groupby("TeamId")["TeamRaceAvgFinish"]
        .transform(
            lambda x: x.shift(1).expanding().mean()
        )
    )

    # Keep only the information needed for merging
    team_history = team_race_performance[
        [
            "Year",
            "Round",
            "TeamId",
            "TeamHistoricalAvgFinish"
        ]
    ]

    # Merge historical team performance back into driver-level data
    driver_race = driver_race.merge(
        team_history,
        on=["Year", "Round", "TeamId"],
        how="left",
        validate="many_to_one"
    )

    return driver_race

if __name__ == "__main__":

    race, qualifying = load_data()

    driver_race = create_driver_race_dataset(
        race,
        qualifying
    )

    print(
        driver_race[
            [
                "Year",
                "Round",
                "Race",
                "FullName",
                "BestQualifyingTime",
                "QualifyingTimeGap"
            ]
        ].head(20)
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "driver_race_features.csv"
    )

    driver_race.to_csv(
        output_file,
        index=False
    )

    print("Feature engineering completed.")
    print(f"Rows: {len(driver_race)}")
    print(f"Columns: {len(driver_race.columns)}")
    print(f"Saved to: {output_file}")