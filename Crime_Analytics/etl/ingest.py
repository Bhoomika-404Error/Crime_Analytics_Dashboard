"""
India Crime Analytics ETL

Usage:
    python etl/ingest.py
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "india_crime_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def truncate_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE crime_city_year, crime_state_year RESTART IDENTITY;")
    conn.commit()


def load_state_year(conn, df: pd.DataFrame) -> None:
    rows = [
        tuple(r)
        for r in df[
            [
                "state",
                "year",
                "crime_category",
                "population_lakh",
                "cases_reported",
                "crime_rate_per_100k",
                "solved_cases",
                "charge_sheet_rate",
                "women_victim_share",
                "severity_index",
                "yoy_change_pct",
            ]
        ].itertuples(index=False)
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO crime_state_year (
                state, year, crime_category, population_lakh, cases_reported,
                crime_rate_per_100k, solved_cases, charge_sheet_rate,
                women_victim_share, severity_index, yoy_change_pct
            ) VALUES %s
            """,
            rows,
        )
    conn.commit()


def load_city_year(conn, df: pd.DataFrame) -> None:
    rows = [
        tuple(r)
        for r in df[
            [
                "state",
                "city",
                "year",
                "cases_reported",
                "crime_rate_per_100k",
                "detection_rate",
                "women_helpdesk_coverage",
                "cyber_crime_share",
                "severity_index",
            ]
        ].itertuples(index=False)
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO crime_city_year (
                state, city, year, cases_reported, crime_rate_per_100k,
                detection_rate, women_helpdesk_coverage, cyber_crime_share, severity_index
            ) VALUES %s
            """,
            rows,
        )
    conn.commit()


def run() -> None:
    state_df = pd.read_csv(DATA_DIR / "crime_state_year.csv")
    city_df = pd.read_csv(DATA_DIR / "crime_city_year.csv")
    conn = get_connection()
    truncate_tables(conn)
    load_state_year(conn, state_df)
    load_city_year(conn, city_df)
    conn.close()
    print("Crime analytics data loaded into PostgreSQL.")


if __name__ == "__main__":
    run()
