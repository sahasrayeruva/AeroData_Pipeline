
import sqlite3

DATABASE_FILE = "data/database/aerodata.db"


def run_queries():

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    print("\n========== SQL DATABASE TESTING ==========")

    # Query 1: Total airports
    cursor.execute("SELECT COUNT(*) FROM airports")
    print("\nTotal airports:", cursor.fetchone()[0])

    # Query 2: Total routes
    cursor.execute("SELECT COUNT(*) FROM routes")
    print("Total routes:", cursor.fetchone()[0])

    # Query 3: Airports by country
    cursor.execute("""
        SELECT country, COUNT(*) AS total
        FROM airports
        GROUP BY country
        ORDER BY total DESC
        LIMIT 10
    """)

    print("\nTop 10 countries by airport count:")

    for row in cursor.fetchall():
        print(row)

    # Query 4: Airports with the most outgoing routes
    cursor.execute("""
        SELECT a.name, a.country, COUNT(r.route_id) AS total_routes
        FROM airports a
        JOIN routes r
        ON a.airport_id = r.source_airport_id
        GROUP BY a.airport_id, a.name, a.country
        ORDER BY total_routes DESC
        LIMIT 10
    """)

    print("\nTop 10 airports by outgoing routes:")

    for row in cursor.fetchall():
        print(row)

    # Query 5: Sample routes with airport names
    cursor.execute("""
        SELECT
            source.name,
            destination.name,
            r.airline,
            r.stops
        FROM routes r
        JOIN airports source
        ON r.source_airport_id = source.airport_id
        JOIN airports destination
        ON r.destination_airport_id = destination.airport_id
        LIMIT 10
    """)

    print("\nSample airline routes:")

    for row in cursor.fetchall():
        print(row)

    connection.close()

    print("\nSQL QUERY TESTING COMPLETED!")


if __name__ == "__main__":
    run_queries()
