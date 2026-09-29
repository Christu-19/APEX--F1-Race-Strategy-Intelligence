import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = (
    PROJECT_DIR / "data" / "processed"
)


def create_race_summary():

    race_results = pd.read_csv(
        PROCESSED_DIR / "cleaned_race_results.csv"
    )

    qualifying = pd.read_csv(
        PROCESSED_DIR / "cleaned_qualifying_results.csv"
    )

    # --------------------------------------------------
    # Basic race information
    # --------------------------------------------------

    race_summary = (
        race_results
        .groupby(
            ["Year", "Race"],
            as_index=False
        )
        .agg(
            TotalDrivers=("DriverId", "count"),
            TotalLaps=("Laps", "max")
        )
    )

    # --------------------------------------------------
    # Winner
    # --------------------------------------------------

    winners = (
        race_results[
            race_results["Position"] == 1
        ][
            [
                "Year",
                "Race",
                "FullName"
            ]
        ]
        .rename(
            columns={
                "FullName": "Winner"
            }
        )
    )

    # --------------------------------------------------
    # Podium
    # --------------------------------------------------

    podium = race_results[
        race_results["Position"].isin([1, 2, 3])
    ][
        [
            "Year",
            "Race",
            "Position",
            "FullName"
        ]
    ]

    podium_pivot = (
        podium
        .pivot(
            index=["Year", "Race"],
            columns="Position",
            values="FullName"
        )
        .reset_index()
        .rename(
            columns={
                1: "Winner",
                2: "Second",
                3: "Third"
            }
        )
    )

    # --------------------------------------------------
    # Pole position
    # --------------------------------------------------

    pole = (
        qualifying[
            qualifying["Position"] == 1
        ][
            [
                "Year",
                "Race",
                "FullName"
            ]
        ]
        .rename(
            columns={
                "FullName": "PoleDriver"
            }
        )
    )

    # --------------------------------------------------
    # Merge everything
    # --------------------------------------------------

    race_summary = race_summary.merge(
        podium_pivot,
        on=["Year", "Race"],
        how="left"
    )

    race_summary = race_summary.merge(
        pole,
        on=["Year", "Race"],
        how="left"
    )

    # --------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------

    race_summary = race_summary.sort_values(
        ["Year", "Race"]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    output_file = (
        PROCESSED_DIR / "race_summary.csv"
    )

    race_summary.to_csv(
        output_file,
        index=False
    )

    print("Race summary created successfully!")
    print(f"Rows: {len(race_summary)}")
    print(f"Columns: {len(race_summary.columns)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    create_race_summary()