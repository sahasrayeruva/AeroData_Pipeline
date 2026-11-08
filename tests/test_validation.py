
import pandas as pd

from src.validation.validation_engine import (
    validate_airports,
    validate_routes
)


def make_airports():
    return pd.DataFrame({
        "airport_id": [1, 2],
        "name": ["Airport A", "Airport B"],
        "city": ["City A", "City B"],
        "country": ["India", "India"],
        "iata": ["AAA", "BBB"],
        "icao": ["AAAA", "BBBB"],
        "latitude": [12.0, 13.0],
        "longitude": [77.0, 78.0],
        "altitude": [100, 200],
        "timezone": [5.5, 5.5],
        "dst": ["N", "N"],
        "tz_database": ["Asia/Kolkata", "Asia/Kolkata"],
        "type": ["airport", "airport"],
        "source": ["Test", "Test"]
    })


def make_routes():
    return pd.DataFrame({
        "airline": ["AA"],
        "airline_id": [10],
        "source_airport": ["AAA"],
        "source_airport_id": [1],
        "destination_airport": ["BBB"],
        "destination_airport_id": [2],
        "codeshare": ["Y"],
        "stops": [0],
        "equipment": ["320"]
    })


def test_duplicate_airport_id():
    airports = make_airports()
    airports.loc[1, "airport_id"] = 1

    clean, rejected, flagged = validate_airports(airports)

    assert len(rejected) == 1
    assert "VAL-01" in rejected.iloc[0]["rejected_reasons"]


def test_missing_airport_name():
    airports = make_airports()
    airports.loc[0, "name"] = None

    clean, rejected, flagged = validate_airports(airports)

    assert len(rejected) == 1
    assert "VAL-02" in rejected.iloc[0]["rejected_reasons"]


def test_invalid_latitude():
    airports = make_airports()
    airports.loc[0, "latitude"] = 100

    clean, rejected, flagged = validate_airports(airports)

    assert len(rejected) == 1
    assert "VAL-03" in rejected.iloc[0]["rejected_reasons"]


def test_invalid_longitude():
    airports = make_airports()
    airports.loc[0, "longitude"] = 200

    clean, rejected, flagged = validate_airports(airports)

    assert len(rejected) == 1
    assert "VAL-04" in rejected.iloc[0]["rejected_reasons"]


def test_duplicate_airport_name_is_flagged():
    airports = make_airports()
    airports.loc[1, "name"] = "Airport A"

    clean, rejected, flagged = validate_airports(airports)

    assert len(rejected) == 0
    assert len(flagged) == 2
    assert "VAL-05" in flagged.iloc[0]["flagged_reasons"]


def test_invalid_iata_is_flagged():
    airports = make_airports()
    airports.loc[0, "iata"] = "INVALID"

    clean, rejected, flagged = validate_airports(airports)

    assert len(rejected) == 0
    assert "VAL-06" in flagged.iloc[0]["flagged_reasons"]


def test_unknown_source_airport():
    routes = make_routes()
    airports = make_airports()

    routes.loc[0, "source_airport_id"] = 999

    clean, rejected, flagged = validate_routes(routes, airports)

    assert len(rejected) == 1
    assert "VAL-07" in rejected.iloc[0]["rejected_reasons"]


def test_missing_destination_airport():
    routes = make_routes()
    airports = make_airports()

    routes.loc[0, "destination_airport_id"] = None

    clean, rejected, flagged = validate_routes(routes, airports)

    assert len(rejected) == 1
    assert "VAL-08" in rejected.iloc[0]["rejected_reasons"]


def test_negative_route_stops():
    routes = make_routes()
    airports = make_airports()

    routes.loc[0, "stops"] = -1

    clean, rejected, flagged = validate_routes(routes, airports)

    assert len(rejected) == 1
    assert "VAL-09" in rejected.iloc[0]["rejected_reasons"]


def test_missing_optional_field_is_flagged():
    routes = make_routes()
    airports = make_airports()

    routes.loc[0, "codeshare"] = None

    clean, rejected, flagged = validate_routes(routes, airports)

    assert len(rejected) == 0
    assert len(flagged) == 1
    assert "VAL-10" in flagged.iloc[0]["flagged_reasons"]
