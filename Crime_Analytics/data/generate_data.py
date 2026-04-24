from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd


random.seed(7)
np.random.seed(7)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

YEARS = list(range(2014, 2024))
STATES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Noida"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Kota"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh"],
}

CATEGORIES = {
    "Violent Crime": (0.82, 32, 66, 22),
    "Property Crime": (1.15, 58, 54, 9),
    "Cyber Crime": (1.42, 18, 48, 11),
    "Crimes Against Women": (1.21, 37, 61, 25),
    "Economic Offences": (1.09, 21, 52, 15),
}

STATE_WEIGHT = {
    "Maharashtra": 1.32,
    "Delhi": 1.24,
    "Karnataka": 1.16,
    "Tamil Nadu": 1.12,
    "Uttar Pradesh": 1.28,
    "West Bengal": 1.07,
    "Gujarat": 1.04,
    "Rajasthan": 0.98,
    "Madhya Pradesh": 1.03,
    "Telangana": 1.08,
    "Bihar": 0.95,
    "Punjab": 0.92,
    "Kerala": 0.88,
    "Odisha": 0.87,
    "Assam": 0.84,
}

BASE_POPULATION_M = {
    "Maharashtra": 124,
    "Delhi": 20,
    "Karnataka": 70,
    "Tamil Nadu": 78,
    "Uttar Pradesh": 232,
    "West Bengal": 100,
    "Gujarat": 71,
    "Rajasthan": 81,
    "Madhya Pradesh": 87,
    "Telangana": 40,
    "Bihar": 127,
    "Punjab": 31,
    "Kerala": 36,
    "Odisha": 47,
    "Assam": 36,
}


def build_state_year() -> pd.DataFrame:
    rows = []
    for state, cities in STATES.items():
        state_factor = STATE_WEIGHT[state]
        base_pop = BASE_POPULATION_M[state]
        for year in YEARS:
            year_factor = 1 + ((year - YEARS[0]) * 0.028)
            population = round(base_pop * (1 + ((year - YEARS[0]) * 0.011)), 2)
            for category, params in CATEGORIES.items():
                trend_factor, base_rate, solve_base, severity_base = params
                noise = np.random.normal(1.0, 0.08)
                rate = max(8, base_rate * state_factor * year_factor * trend_factor * noise)
                cases = int(rate * population * 10)
                solved = int(cases * np.clip((solve_base + np.random.normal(0, 5)) / 100, 0.28, 0.82))
                charge_sheet_rate = np.clip(solve_base + np.random.normal(3, 6), 32, 91)
                women_share = np.clip(
                    18 + (12 if category == "Crimes Against Women" else 0) + np.random.normal(4, 5),
                    4,
                    64,
                )
                severity = np.clip(severity_base + (rate / 7) + np.random.normal(0, 4), 8, 96)
                rows.append(
                    {
                        "state": state,
                        "year": year,
                        "crime_category": category,
                        "population_lakh": round(population * 10, 2),
                        "cases_reported": cases,
                        "crime_rate_per_100k": round(rate, 2),
                        "solved_cases": solved,
                        "charge_sheet_rate": round(charge_sheet_rate, 2),
                        "women_victim_share": round(women_share, 2),
                        "severity_index": round(severity, 2),
                    }
                )

    df = pd.DataFrame(rows).sort_values(["state", "crime_category", "year"]).reset_index(drop=True)
    df["previous_year_cases"] = df.groupby(["state", "crime_category"])["cases_reported"].shift(1)
    df["yoy_change_pct"] = np.where(
        df["previous_year_cases"].fillna(0) > 0,
        ((df["cases_reported"] - df["previous_year_cases"]) / df["previous_year_cases"]) * 100,
        0,
    )
    df["yoy_change_pct"] = df["yoy_change_pct"].round(2)
    return df.drop(columns=["previous_year_cases"])


def build_city_year(state_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for state, cities in STATES.items():
        state_rows = state_df[state_df["state"] == state]
        for year in YEARS:
            year_rows = state_rows[state_rows["year"] == year]
            state_total = int(year_rows["cases_reported"].sum())
            city_weights = np.random.dirichlet(np.ones(len(cities)) * 1.3)
            state_rate = float(year_rows["crime_rate_per_100k"].mean())
            for city, weight in zip(cities, city_weights):
                cases = int(state_total * weight)
                rate = max(10, state_rate * np.random.uniform(0.76, 1.28))
                detection = np.clip(np.random.normal(59, 10), 28, 91)
                women_helpdesk = np.clip(np.random.normal(72, 8), 41, 97)
                cyber_share = np.clip(np.random.normal(11, 4), 2, 28)
                severity = np.clip((rate / 2.4) + (100 - detection) / 3 + np.random.normal(7, 4), 12, 98)
                rows.append(
                    {
                        "state": state,
                        "city": city,
                        "year": year,
                        "cases_reported": cases,
                        "crime_rate_per_100k": round(rate, 2),
                        "detection_rate": round(detection, 2),
                        "women_helpdesk_coverage": round(women_helpdesk, 2),
                        "cyber_crime_share": round(cyber_share, 2),
                        "severity_index": round(severity, 2),
                    }
                )
    return pd.DataFrame(rows).sort_values(["state", "city", "year"]).reset_index(drop=True)


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    state_year = build_state_year()
    city_year = build_city_year(state_year)
    state_year.to_csv(DATA_DIR / "crime_state_year.csv", index=False)
    city_year.to_csv(DATA_DIR / "crime_city_year.csv", index=False)
    print(f"Saved {len(state_year)} state-year-category records")
    print(f"Saved {len(city_year)} city-year records")
