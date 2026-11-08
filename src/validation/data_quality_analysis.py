
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


def load_data():

    airports = pd.read_csv(
        DATA_DIR / "airports.dat",
        header=None,
        names=AIRPORT_COLUMNS,
        na_values=[r"\N"]
    )

    routes = pd.read_csv(
        DATA_DIR / "routes.dat",
        header=None,
        names=ROUTE_COLUMNS,
        na_values=[r"\N"]
    )

    return airports, routes


def analyze_airports(airports):

    print("\n========== AIRPORT ANALYSIS ==========")

    print("Duplicate airport IDs:",
          airports["airport_id"].duplicated().sum())

    print("Duplicate airport names:",
          airports["name"].duplicated().sum())

    print("Invalid latitude:",
          ((airports["latitude"] < -90) |
           (airports["latitude"] > 90)).sum())

    print("Invalid longitude:",
          ((airports["longitude"] < -180) |
           (airports["longitude"] > 180)).sum())

    print("Missing airport names:",
          airports["name"].isna().sum())

    print("Missing airport IDs:",
          airports["airport_id"].isna().sum())


def analyze_routes(routes, airports):

    print("\n========== ROUTE ANALYSIS ==========")

    print("Duplicate route records:",
          routes.duplicated().sum())

    print("Negative stops:",
          (routes["stops"] < 0).sum())

    print("Missing source airport IDs:",
          routes["source_airport_id"].isna().sum())

    print("Missing destination airport IDs:",
          routes["destination_airport_id"].isna().sum())

    valid_ids = set(airports["airport_id"])

    source_ids = routes["source_airport_id"].dropna()
    destination_ids = routes["destination_airport_id"].dropna()

    print("Unknown source airport IDs:",
          (~source_ids.isin(valid_ids)).sum())

    print("Unknown destination airport IDs:",
          (~destination_ids.isin(valid_ids)).sum())


if __name__ == "__main__":

    airports, routes = load_data()

    analyze_airports(airports)
    analyze_routes(routes, airports)

    print("\nDATA QUALITY ANALYSIS COMPLETED!")
