
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

AIRPORT_COLUMNS = [
    "airport_id", "name", "city", "country",
    "iata", "icao", "latitude", "longitude",
    "altitude", "timezone", "dst", "tz_database",
    "type", "source"
]

ROUTE_COLUMNS = [
    "airline", "airline_id", "source_airport",
    "source_airport_id", "destination_airport",
    "destination_airport_id", "codeshare",
    "stops", "equipment"
]


def inspect_dataset(filename, columns):

    file_path = DATA_DIR / filename

    df = pd.read_csv(
        file_path,
        header=None,
        names=columns,
        na_values=[r"\N"],
        keep_default_na=True,
        encoding="utf-8"
    )

    print("\n" + "=" * 55)
    print(f"DATASET: {filename}")
    print("=" * 55)

    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst 5 records:")
    print(df.head().to_string(index=False))

    return df


if __name__ == "__main__":

    airports = inspect_dataset(
        "airports.dat", AIRPORT_COLUMNS
    )

    routes = inspect_dataset(
        "routes.dat", ROUTE_COLUMNS
    )

    print("\nDATASET INSPECTION COMPLETED!")
