
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from src.logging_config import setup_logger

PROCESSED_DIR = Path("data/processed")
DATABASE_FILE = Path("data/database/aerodata.db")
REPORT_DIR = Path("reports")

def count_reasons(df, column):

    if column not in df.columns:
        return {}

    reasons = (
        df[column]
        .dropna()
        .astype(str)
        .str.split("; ")
        .explode()
    )

    reasons = reasons[reasons != ""]

    return reasons.value_counts().to_dict()



def generate_report():

    logger = setup_logger()

    try:
        logger.info("Validation report generation started")

        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Loading processed datasets")

        airports = pd.read_csv(
            PROCESSED_DIR / "clean_airports.csv"
        )
        rejected_airports = pd.read_csv(
            PROCESSED_DIR / "rejected_airports.csv"
        )
        flagged_airports = pd.read_csv(
            PROCESSED_DIR / "flagged_airports.csv"
        )

        routes = pd.read_csv(
            PROCESSED_DIR / "clean_routes.csv"
        )
        rejected_routes = pd.read_csv(
            PROCESSED_DIR / "rejected_routes.csv"
        )
        flagged_routes = pd.read_csv(
            PROCESSED_DIR / "flagged_routes.csv"
        )

        logger.info(
            "Datasets loaded | Clean airports=%d | Clean routes=%d",
            len(airports), len(routes)
        )

        # Database verification
        logger.info("Checking database integrity")

        with sqlite3.connect(DATABASE_FILE) as connection:

            cursor = connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM airports")
            database_airports = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM routes")
            database_routes = cursor.fetchone()[0]

            cursor.execute("PRAGMA foreign_key_check")
            foreign_key_errors = cursor.fetchall()

        if foreign_key_errors:
            logger.error(
                "Database foreign key check FAILED: %d violations",
                len(foreign_key_errors)
            )
        else:
            logger.info("Database foreign key check PASSED")

        airport_reasons = count_reasons(
            rejected_airports, "rejected_reasons"
        )

        route_reasons = count_reasons(
            rejected_routes, "rejected_reasons"
        )

        airport_flags = count_reasons(
            flagged_airports, "flagged_reasons"
        )

        route_flags = count_reasons(
            flagged_routes, "flagged_reasons"
        )

        report = []

        report.append("# AeroData Pipeline - Validation Report")
        report.append("")
        report.append(
            f"Generated: {datetime.now(timezone.utc).isoformat()}"
        )
        report.append("")
        report.append("## 1. Executive Summary")
        report.append("")
        report.append(
            "This report summarizes the results of aviation "
            "data ingestion, validation and database generation."
        )

        report.append("")
        report.append("## 2. Airport Dataset")
        report.append("")
        report.append("| Metric | Count |")
        report.append("|---|---:|")
        report.append(f"| Accepted | {len(airports)} |")
        report.append(f"| Rejected | {len(rejected_airports)} |")
        report.append(f"| Flagged | {len(flagged_airports)} |")
        report.append("")

        report.append("### Airport Rejection Reasons")
        report.append("")

        if airport_reasons:
            for reason, count in airport_reasons.items():
                report.append(f"- {reason}: {count}")
        else:
            report.append("No airport records rejected.")

        report.append("")
        report.append("### Airport Flag Reasons")
        report.append("")

        for reason, count in airport_flags.items():
            report.append(f"- {reason}: {count}")

        report.append("")
        report.append("## 3. Route Dataset")
        report.append("")
        report.append("| Metric | Count |")
        report.append("|---|---:|")
        report.append(f"| Accepted | {len(routes)} |")
        report.append(f"| Rejected | {len(rejected_routes)} |")
        report.append(f"| Flagged | {len(flagged_routes)} |")
        report.append("")

        report.append("### Route Rejection Reasons")
        report.append("")

        for reason, count in route_reasons.items():
            report.append(f"- {reason}: {count}")

        report.append("")
        report.append("### Route Flag Reasons")
        report.append("")

        for reason, count in route_flags.items():
            report.append(f"- {reason}: {count}")

        report.append("")
        report.append("## 4. Database Verification")
        report.append("")
        report.append("| Metric | Result |")
        report.append("|---|---:|")
        report.append(f"| Airport records inserted | {database_airports} |")
        report.append(f"| Route records inserted | {database_routes} |")
        report.append(
            f"| Foreign key integrity | "
            f"{'PASS' if not foreign_key_errors else 'FAIL'} |"
        )

        report.append("")
        report.append("## 5. Validation Rules")
        report.append("")
        report.append("| Rule | Description |")
        report.append("|---|---|")

        rules = [
            ("VAL-01", "Unique airport IDs"),
            ("VAL-02", "Mandatory airport names"),
            ("VAL-03", "Valid latitude range"),
            ("VAL-04", "Valid longitude range"),
            ("VAL-05", "Duplicate airport name detection"),
            ("VAL-06", "IATA code format"),
            ("VAL-07", "Source airport reference integrity"),
            ("VAL-08", "Destination airport reference integrity"),
            ("VAL-09", "Non-negative route stops"),
            ("VAL-10", "Missing optional fields detection")
        ]

        for rule_id, description in rules:
            report.append(f"| {rule_id} | {description} |")

        report.append("")
        report.append("## 6. Final Result")
        report.append("")

        if not foreign_key_errors:
            report.append("**Database verification: PASSED**")
        else:
            report.append("**Database verification: FAILED**")

        report.append("")
        report.append(
            "Note: This project uses historical OpenFlights "
            "data for educational software engineering purposes. "
            "It is not an operational aviation navigation database."
        )

        report_path = REPORT_DIR / "validation_report.md"

        report_path.write_text(
            "\n".join(report),
            encoding="utf-8"
        )

        print("Validation report generated successfully!")
        print(f"Location: {report_path}")

        logger.info(
            "Validation report generated successfully: %s",
            report_path
        )

    except Exception:
        logger.exception("Validation report generation failed")
        raise


if __name__ == "__main__":
    generate_report()
