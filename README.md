# AeroData Pipeline 

**A Reproducible Aviation Data Engineering and Validation Pipeline**

AeroData Pipeline is a Python-based data engineering project designed to ingest, inspect, validate, clean, and store aviation datasets. It applies rule-based data quality checks, maintains rejected and flagged records, verifies database integrity, and generates automated validation reports.

## Project Objectives

- Build a reproducible aviation data processing pipeline.
- Implement rule-based validation using defined requirements.
- Separate clean, rejected, and flagged records.
- Store validated aviation data in a relational SQLite database.
- Verify database relationships and integrity.
- Generate automated data quality reports.
- Maintain execution logs for traceability.

##  Architecture

```text
OpenFlights Raw Datasets
          |
          v
    Data Ingestion
          |
          v
   Validation Engine
          |
    +-----+------+
    |     |      |
  Clean Reject Flagged
    | 
    v
 SQLite Database
    |
    v
 Database Verification
    |
    v
 Validation Report
    |
    v
 Execution Logs
```

##  Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Pipeline implementation |
| Pandas | Data processing |
| SQLite | Relational database |
| Pytest | Automated testing |
| Logging | Execution traceability |
| Git | Version control |

##  Project Structure

```text
AeroData-Pipeline/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── database/
│
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── validation/
│   ├── database/
│   ├── versioning/
│   └── logging_config.py
│
├── tests/
├── reports/
├── releases/
├── docs/
├── logs/
│
├── run_pipeline.py
├── requirements.txt
├── DECISIONS.md
└── README.md
```

##  Dataset

This project uses historical aviation datasets from OpenFlights:

- `airports.dat` – Airport information and geographic details.
- `routes.dat` – Airline route information.

Source: [OpenFlights Data](https://openflights.org/data)

The datasets are historical and are used for educational and software engineering purposes.

## Data Validation Rules

The pipeline implements 10 validation rules:

| Rule ID | Validation |
|---|---|
| VAL-01 | Unique airport IDs |
| VAL-02 | Mandatory airport names |
| VAL-03 | Valid latitude range |
| VAL-04 | Valid longitude range |
| VAL-05 | Duplicate airport name detection |
| VAL-06 | IATA code format |
| VAL-07 | Source airport reference integrity |
| VAL-08 | Destination airport reference integrity |
| VAL-09 | Non-negative route stops |
| VAL-10 | Missing optional fields detection |

Records are classified into:

- **Clean:** Records that pass rejection rules.
- **Rejected:** Records that violate mandatory validation rules.
- **Flagged:** Records requiring additional review.

A flagged record can also be part of the clean dataset if it passes all rejection rules.

##  Current Processing Results

| Metric | Result |
|---|---:|
| Total airports | 7,698 |
| Total routes | 67,663 |
| Clean airports | 7,698 |
| Rejected airports | 0 |
| Flagged airports | 1,687 |
| Clean routes | 66,771 |
| Rejected routes | 892 |
| Flagged routes | 53,074 |
| Database airports | 7,698 |
| Database routes | 66,771 |

##  Installation and Execution

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AeroData-Pipeline
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the datasets

Download the following files into `data/raw/`:

- [airports.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat)
- [routes.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat)

### 5. Run the complete pipeline

```bash
python run_pipeline.py
```

### 6. Run automated tests

```bash
python -m pytest -v
```

## Database Design

The SQLite database contains two primary tables:

**Airports**
- Airport ID (Primary Key)
- Airport name
- City and country
- IATA and ICAO codes
- Latitude and longitude
- Additional airport metadata

**Routes**
- Route ID (Primary Key)
- Airline information
- Source airport ID (Foreign Key)
- Destination airport ID (Foreign Key)
- Number of stops
- Aircraft equipment information

Database indexes are created to support efficient airport and route lookups.

## Validation Reports

The pipeline automatically generates:

`reports/validation_report.md`

The report contains:
- Dataset processing statistics.
- Rejection reasons.
- Flagged record summaries.
- Database record counts.
- Foreign-key integrity results.
- Validation rule descriptions.

## Logging and Traceability

The logging system records:

- Pipeline execution start and completion.
- Dataset loading operations.
- Validation results.
- Database creation and verification.
- Report generation.
- Warnings and errors.

Each execution is associated with a Run ID to help trace pipeline activity.

##  Testing

Automated tests are implemented using Pytest to verify the validation rules.

Current test result: **10 tests passed.**

##  Scope and Limitations

- OpenFlights data is historical and should not be treated as current operational aviation data.
- This project is intended for educational and software engineering purposes.
- It is not certified for operational aviation navigation.
- The project does not claim DO-178C or DO-200 compliance.

## Project Completion Status

**AeroData Pipeline v0.1 — Initial Release**

The initial release is complete and includes the following implemented features:

- [x] Dataset ingestion and inspection
- [x] Rule-based data validation
- [x] Clean, rejected, and flagged data separation
- [x] SQLite database generation
- [x] Database integrity verification
- [x] Automated validation reports
- [x] Execution logging with run identification
- [x] One-command pipeline execution
- [x] Unit tests for validation rules
- [x] Project documentation

## Author

Developed as an aviation data engineering and software verification portfolio project.

---

**AeroData Pipeline v0.1 — Building reliable, traceable, and reproducible aviation data workflows.**