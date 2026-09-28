import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_DIR / "data" / "processed"


# Load cleaned datasets
race = pd.read_csv(
    PROCESSED_DATA_DIR / "cleaned_race_results.csv"
)

qualifying = pd.read_csv(
    PROCESSED_DATA_DIR / "cleaned_qualifying_results.csv"
)


print("Race data loaded:", race.shape)
print("Qualifying data loaded:", qualifying.shape)

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


qualifying_features= qualifying_features.rename(
    columns={
        "Position":"QualifyingPosition"
    }
)

print(qualifying_features.columns.to_list())

# Remove qualifying records without a DriverId
qualifying_features = qualifying_features.dropna(
    subset=["DriverId"]
)

print("\nQualifying features after removing missing DriverId:")
print("Rows:", len(qualifying_features))
print("Missing DriverId:", qualifying_features["DriverId"].isna().sum())

# Merge qualifying data with race results
driver_race = race.merge(
    qualifying_features,
    on=["Year", "Race", "DriverId"],
    how="left",
    validate="one_to_one"
)

print("\nMerged driver-race dataset:")
print("Rows:", len(driver_race))
print("Columns:", len(driver_race.columns))

# Create best qualifying lap time
driver_race["BestQualifyingTime"] = driver_race[
    ["Q1", "Q2", "Q3"]
].min(axis=1)

print("\nBest qualifying time created.")

print(
    driver_race[
        [
            "FullName",
            "QualifyingPosition",
            "Q1",
            "Q2",
            "Q3",
            "BestQualifyingTime"
        ]
    ].head()
)

# Save dataset
output_file = PROCESSED_DATA_DIR / "driver_race_features.csv"

driver_race.to_csv(
    output_file,
    index=False
)

print("\nFeature-engineered dataset saved.")
print("Output:", output_file)
print("Final shape:", driver_race.shape)
