
import sqlite3
import pandas as pd
from pathlib import Path
from src.logging_config import setup_logger

PROCESSED_DIR = Path("data/processed")
DATABASE_DIR = Path("data/database")

DATABASE_FILE = DATABASE_DIR / "aerodata.db"


def create_database(connection):

    cursor = connection.cursor()

    # Airport table
    cursor.execute("""
        CREATE TABLE airports (
            airport_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT NOT NULL,
            iata TEXT,
            icao TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            altitude INTEGER,
            timezone REAL,
            dst TEXT,
            tz_database TEXT,
            type TEXT,
            source TEXT
        )
    """)

    # Route table
    cursor.execute("""
        CREATE TABLE routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline TEXT NOT NULL,
            airline_id INTEGER,
            source_airport TEXT NOT NULL,
            source_airport_id INTEGER NOT NULL,
            destination_airport TEXT NOT NULL,
            destination_airport_id INTEGER NOT NULL,
            codeshare TEXT,
            stops INTEGER NOT NULL,
            equipment TEXT,

            FOREIGN KEY (source_airport_id)
                REFERENCES airports(airport_id),

            FOREIGN KEY (destination_airport_id)
                REFERENCES airports(airport_id)
        )
    """)

    # Indexes for faster searches
    cursor.execute("""
        CREATE INDEX idx_route_source
        ON routes(source_airport_id)
    """)

    cursor.execute("""
        CREATE INDEX idx_route_destination
        ON routes(destination_airport_id)
    """)

    cursor.execute("""
        CREATE INDEX idx_airport_iata
        ON airports(iata)
    """)

    connection.commit()

    print("Database schema created successfully!")


def insert_records(connection, table, dataframe):

    columns = list(dataframe.columns)

    placeholders = ", ".join(["?"] * len(columns))
    column_names = ", ".join(columns)

    query = (
        f"INSERT INTO {table} "
        f"({column_names}) VALUES ({placeholders})"
    )

    records = []

    for row in dataframe.itertuples(index=False, name=None):
        values = tuple(
            None if pd.isna(value) else value
            for value in row
        )
        records.append(values)

    connection.executemany(query, records)
    connection.commit()

    print(f"Inserted {len(records)} records into {table}")



def verify_database(connection, logger):

    cursor = connection.cursor()

    print("\n========== DATABASE VERIFICATION ==========")
    logger.info("Database verification started")

    for table in ["airports", "routes"]:

        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        print(f"{table}: {count} records")
        logger.info("%s table contains %d records", table, count)

    # Check foreign key integrity
    cursor.execute("PRAGMA foreign_key_check")
    errors = cursor.fetchall()

    if errors:
        print("Foreign key violations:", errors)
        logger.error("Foreign key integrity FAILED: %d violations", len(errors))
        raise sqlite3.IntegrityError(
            f"Foreign key integrity failed: {len(errors)} violations"
        )
    else:
        print("Foreign key integrity: PASSED")
        logger.info("Foreign key integrity check PASSED")

    # Check table structure
    cursor.execute("PRAGMA table_info(airports)")
    print("\nAirport table columns:")

    for column in cursor.fetchall():
        print(column[1], column[2])

    logger.info("Database verification completed successfully")




def main():

    logger = setup_logger()

    try:
        logger.info("Database creation process started")

        DATABASE_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Loading clean datasets")

        airports = pd.read_csv(
            PROCESSED_DIR / "clean_airports.csv"
        )

        routes = pd.read_csv(
            PROCESSED_DIR / "clean_routes.csv"
        )

        logger.info(
            "Clean datasets loaded | Airports=%d | Routes=%d",
            len(airports), len(routes)
        )

        # Remove inspection/validation metadata
        airports = airports.drop(
            columns=["source_row", "rejected_reasons",
                     "flagged_reasons"],
            errors="ignore"
        )

        routes = routes.drop(
            columns=["source_row", "rejected_reasons",
                     "flagged_reasons"],
            errors="ignore"
        )

        # Rebuild database for a reproducible run
        if DATABASE_FILE.exists():
            DATABASE_FILE.unlink()
            logger.info("Previous database removed")

        connection = sqlite3.connect(DATABASE_FILE)

        try:
            connection.execute("PRAGMA foreign_keys = ON")

            logger.info("Creating database schema")
            create_database(connection)

            logger.info("Inserting airport records")
            insert_records(connection, "airports", airports)

            logger.info("Inserting route records")
            insert_records(connection, "routes", routes)

            logger.info("Starting database verification")
            verify_database(connection, logger)

            print("\nDATABASE CREATED SUCCESSFULLY!")
            print(f"Database location: {DATABASE_FILE}")

            logger.info(
                "Database created successfully at %s",
                DATABASE_FILE
            )

        except Exception:
            connection.rollback()
            logger.exception("Database operation failed")
            raise

        finally:
            connection.close()

    except Exception:
        logger.exception("Database creation process failed")
        raise


if __name__ == "__main__":
    main()
