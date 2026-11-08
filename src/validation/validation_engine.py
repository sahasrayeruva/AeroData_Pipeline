
import pandas as pd
import re
from pathlib import Path
from src.logging_config import setup_logger

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

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


def validate_airports(airports):

    df = airports.copy()

    # Store original source row numbers (1-based)
    df.insert(0, "source_row", range(1, len(df) + 1))

    rejected_reasons = [[] for _ in range(len(df))]
    flagged_reasons = [[] for _ in range(len(df))]

    # VAL-01: Airport IDs must be unique
    duplicate_ids = (
        df["airport_id"].notna()
        & df["airport_id"].duplicated(keep="first")
    )

    for i in df.index[duplicate_ids]:
        rejected_reasons[i].append("VAL-01: Duplicate airport ID")

    # VAL-02: Airport name must not be missing or blank
    missing_names = (
        df["name"].isna()
        | df["name"].astype("string").str.strip().eq("").fillna(True)
    )

    for i in df.index[missing_names]:
        rejected_reasons[i].append("VAL-02: Missing airport name")

    # VAL-03: Latitude must be between -90 and 90
    latitude = pd.to_numeric(df["latitude"], errors="coerce")

    invalid_latitude = (
        latitude.isna() | ~latitude.between(-90, 90)
    )

    for i in df.index[invalid_latitude]:
        rejected_reasons[i].append("VAL-03: Invalid latitude")

    # VAL-04: Longitude must be between -180 and 180
    longitude = pd.to_numeric(df["longitude"], errors="coerce")

    invalid_longitude = (
        longitude.isna() | ~longitude.between(-180, 180)
    )

    for i in df.index[invalid_longitude]:
        rejected_reasons[i].append("VAL-04: Invalid longitude")

    # VAL-05: Duplicate airport names are flagged
    duplicate_names = (
        df["name"].notna()
        & df["name"].duplicated(keep=False)
    )

    for i in df.index[duplicate_names]:
        flagged_reasons[i].append("VAL-05: Duplicate airport name")

    # VAL-06: IATA code must be three uppercase letters
    iata = df["iata"].astype("string").str.strip()

    invalid_iata = (
        iata.notna()
        & ~iata.str.fullmatch(r"[A-Z]{3}", na=False)
    )

    for i in df.index[invalid_iata]:
        flagged_reasons[i].append("VAL-06: Invalid IATA code")

    # Missing IATA is optional, so it is flagged separately
    missing_iata = iata.isna() | iata.eq("").fillna(False)

    for i in df.index[missing_iata]:
        flagged_reasons[i].append("VAL-06: Missing optional IATA code")

    df["rejected_reasons"] = [
        "; ".join(reasons) for reasons in rejected_reasons
    ]

    df["flagged_reasons"] = [
        "; ".join(reasons) for reasons in flagged_reasons
    ]

    rejected = df[df["rejected_reasons"] != ""].copy()
    clean = df[df["rejected_reasons"] == ""].copy()
    flagged = df[df["flagged_reasons"] != ""].copy()

    return clean, rejected, flagged


def validate_routes(routes, airports):

    df = routes.copy()

    df.insert(0, "source_row", range(1, len(df) + 1))

    rejected_reasons = [[] for _ in range(len(df))]
    flagged_reasons = [[] for _ in range(len(df))]

    valid_airport_ids = set(
        pd.to_numeric(
            airports["airport_id"], errors="coerce"
        ).dropna()
    )

    source_ids = pd.to_numeric(
        df["source_airport_id"], errors="coerce"
    )

    destination_ids = pd.to_numeric(
        df["destination_airport_id"], errors="coerce"
    )

    # VAL-07: Source airport must exist
    missing_source = source_ids.isna()
    unknown_source = (
        source_ids.notna()
        & ~source_ids.isin(valid_airport_ids)
    )

    for i in df.index[missing_source]:
        rejected_reasons[i].append(
            "VAL-07: Missing source airport ID"
        )

    for i in df.index[unknown_source]:
        rejected_reasons[i].append(
            "VAL-07: Unknown source airport ID"
        )

    # VAL-08: Destination airport must exist
    missing_destination = destination_ids.isna()
    unknown_destination = (
        destination_ids.notna()
        & ~destination_ids.isin(valid_airport_ids)
    )

    for i in df.index[missing_destination]:
        rejected_reasons[i].append(
            "VAL-08: Missing destination airport ID"
        )

    for i in df.index[unknown_destination]:
        rejected_reasons[i].append(
            "VAL-08: Unknown destination airport ID"
        )

    # VAL-09: Stops must be non-negative integers
    stops = pd.to_numeric(df["stops"], errors="coerce")

    invalid_stops = (
        stops.isna()
        | (stops < 0)
        | (stops % 1 != 0)
    )

    for i in df.index[invalid_stops]:
        rejected_reasons[i].append(
            "VAL-09: Invalid route stops"
        )

    # VAL-10: Missing optional fields are flagged
    optional_columns = [
        "airline_id", "codeshare", "equipment"
    ]

    for column in optional_columns:
        missing = (
            df[column].isna()
            | df[column].astype("string").str.strip().eq("").fillna(True)
        )

        for i in df.index[missing]:
            flagged_reasons[i].append(
                f"VAL-10: Missing optional {column}"
            )

    df["rejected_reasons"] = [
        "; ".join(reasons) for reasons in rejected_reasons
    ]

    df["flagged_reasons"] = [
        "; ".join(reasons) for reasons in flagged_reasons
    ]

    rejected = df[df["rejected_reasons"] != ""].copy()
    clean = df[df["rejected_reasons"] == ""].copy()
    flagged = df[df["flagged_reasons"] != ""].copy()

    return clean, rejected, flagged


def main():

    logger = setup_logger()

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("AeroData validation pipeline started")

        print("Loading aviation datasets...")
        logger.info("Loading airport and route datasets")

        airports, routes = load_data()

        logger.info(
            "Datasets loaded | Airports=%d | Routes=%d",
            len(airports), len(routes)
        )

        print("Validating airport records...")
        logger.info("Airport validation started")

        clean_airports, rejected_airports, flagged_airports = (
            validate_airports(airports)
        )

        logger.info(
            "Airport validation completed | Clean=%d | Rejected=%d | Flagged=%d",
            len(clean_airports),
            len(rejected_airports),
            len(flagged_airports)
        )

        print("Validating route records...")
        logger.info("Route validation started")

        clean_routes, rejected_routes, flagged_routes = (
            validate_routes(routes, airports)
        )

        logger.info(
            "Route validation completed | Clean=%d | Rejected=%d | Flagged=%d",
            len(clean_routes),
            len(rejected_routes),
            len(flagged_routes)
        )

        # Save processed datasets
        clean_airports.to_csv(
            OUTPUT_DIR / "clean_airports.csv", index=False
        )
        rejected_airports.to_csv(
            OUTPUT_DIR / "rejected_airports.csv", index=False
        )
        flagged_airports.to_csv(
            OUTPUT_DIR / "flagged_airports.csv", index=False
        )
        clean_routes.to_csv(
            OUTPUT_DIR / "clean_routes.csv", index=False
        )
        rejected_routes.to_csv(
            OUTPUT_DIR / "rejected_routes.csv", index=False
        )
        flagged_routes.to_csv(
            OUTPUT_DIR / "flagged_routes.csv", index=False
        )

        logger.info("All processed CSV files saved successfully")

        print("\n========== VALIDATION SUMMARY ==========")

        print("\nAIRPORTS")
        print("Total:", len(airports))
        print("Clean:", len(clean_airports))
        print("Rejected:", len(rejected_airports))
        print("Flagged:", len(flagged_airports))

        print("\nROUTES")
        print("Total:", len(routes))
        print("Clean:", len(clean_routes))
        print("Rejected:", len(rejected_routes))
        print("Flagged:", len(flagged_routes))

        print("\nAll processed files saved in data/processed/")
        print("VALIDATION COMPLETED SUCCESSFULLY!")

        if len(rejected_airports) or len(rejected_routes):
            logger.warning("Some records were rejected during validation")

        if len(flagged_airports) or len(flagged_routes):
            logger.warning("Some records were flagged for review")

        logger.info("AeroData validation pipeline completed successfully")

    except Exception:
        logger.exception("AeroData validation pipeline failed")
        raise


if __name__ == "__main__":
    main()
