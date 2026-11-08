
from src.logging_config import setup_logger
from src.validation.validation_engine import main as run_validation
from src.database.database_builder import main as build_database
from src.validation.report_generator import generate_report


def main():

    logger = setup_logger()

    print("\n======================================")
    print("       AERODATA PIPELINE")
    print("======================================\n")

    logger.info("Complete AeroData pipeline started")

    try:
        # STEP 1: Data validation
        print("\n[STEP 1/3] Running data validation...")
        run_validation()

        # STEP 2: Database creation
        print("\n[STEP 2/3] Building SQLite database...")
        build_database()

        # STEP 3: Report generation
        print("\n[STEP 3/3] Generating validation report...")
        generate_report()

        print("\n======================================")
        print("  AERODATA PIPELINE COMPLETED")
        print("======================================")

        logger.info("Complete AeroData pipeline finished successfully")

    except Exception:
        print("\nPIPELINE FAILED. Check the log file for details.")
        logger.exception("Complete AeroData pipeline failed")
        raise


if __name__ == "__main__":
    main()
