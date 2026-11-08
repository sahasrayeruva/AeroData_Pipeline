
# Data Validation Decisions

Project: AeroData Pipeline

## Purpose

This document records the validation rules and
the decisions applied to aviation datasets.

Original raw datasets will never be modified.

## Airport Validation Rules

| Rule ID | Description | Decision |
|---|---|---|
| VAL-01 | Airport IDs must be unique | Reject duplicate records |
| VAL-02 | Airport names must not be missing | Reject |
| VAL-03 | Latitude must be between -90 and 90 | Reject |
| VAL-04 | Longitude must be between -180 and 180 | Reject |
| VAL-05 | Duplicate airport names | Flag for review |
| VAL-06 | Validate IATA code format when present | Flag invalid values |

## Route Validation Rules

| Rule ID | Description | Decision |
|---|---|---|
| VAL-07 | Source airport ID must reference an existing airport | Reject route |
| VAL-08 | Destination airport ID must reference an existing airport | Reject route |
| VAL-09 | Route stops must be non-negative | Reject route |
| VAL-10 | Missing optional fields | Flag for review |

## Data Handling Decisions

1. Raw input files must remain unchanged.
2. Rejected records must be preserved in quarantine reports.
3. Missing optional fields must not automatically reject records.
4. Duplicate airport names must not be treated as duplicate IDs.
5. Invalid route references must be reported separately.
6. Every validation result must be traceable to its rule ID.
7. Validation reports must include record counts.
8. Clean datasets must be used for database generation.

## Important Limitations

This project uses OpenFlights data for educational
and software engineering purposes.

It is not an operational aviation navigation database.
