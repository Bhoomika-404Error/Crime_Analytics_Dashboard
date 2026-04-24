# India Crime Analytics Dashboard

Portfolio-grade crime intelligence project built in **Streamlit + PostgreSQL** with NCRB-style Indian crime data modeling.

This version ships with high-quality synthetic data shaped like official state-year and city-year crime reporting, so you can run it immediately and later swap in real NCRB tables with the same structure.

## Why this project stands out
- Uses an India-first public policy problem instead of tutorial-style business data
- Designed like an investigative command center, not a generic analytics template
- PostgreSQL-ready schema for CTEs, window functions, yearly comparisons, and ranking queries
- Streamlit UI that feels editorial, tense, and premium enough for a resume showcase

## Project structure
```text
IPL/
|-- dashboard/
|   |-- app.py
|-- data/
|   |-- generate_data.py
|   |-- crime_state_year.csv
|   |-- crime_city_year.csv
|-- db/
|   |-- schema.sql
|-- etl/
|   |-- ingest.py
|-- requirements.txt
```

## Quick start
```bash
pip install -r requirements.txt
python data/generate_data.py
streamlit run dashboard/app.py
```

The app will run even without PostgreSQL by using the generated CSV files.

## PostgreSQL setup
1. Create the database and tables:
```bash
psql -U postgres -f db/schema.sql
```

2. Load the generated CSVs:
```bash
python etl/ingest.py
```

3. Launch the app:
```bash
streamlit run dashboard/app.py
```

## Dashboard features
- National trend line by crime category across 10 years
- State heatmap for category-level pressure mapping
- State ranking by crime rate per 100k
- Category share donut for the latest year
- Deep-dive state explorer with urban hotspot scatter
- Evidence table with rate, solved cases, charge-sheet rate, severity, and YoY change

## Resume bullet
Built an India Crime Trends Analytics pipeline using NCRB-style state and city datasets across 15 states and 10 years; modeled data in PostgreSQL, analyzed annual patterns with SQL-ready metrics, and deployed an interactive Streamlit dashboard with high-impact investigative UI.

## Notes
- Current CSVs are synthetic but realistic and structured for easy replacement with official NCRB extracts.
- Default database name: `india_crime_analytics`
- Default database password in code: `postgres`
