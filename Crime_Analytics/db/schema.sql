CREATE DATABASE india_crime_analytics;
\c india_crime_analytics;

CREATE TABLE IF NOT EXISTS crime_state_year (
    id SERIAL PRIMARY KEY,
    state VARCHAR(80) NOT NULL,
    year INT NOT NULL,
    crime_category VARCHAR(80) NOT NULL,
    population_lakh NUMERIC(10,2) NOT NULL,
    cases_reported INT NOT NULL,
    crime_rate_per_100k NUMERIC(10,2) NOT NULL,
    solved_cases INT NOT NULL,
    charge_sheet_rate NUMERIC(6,2) NOT NULL,
    women_victim_share NUMERIC(6,2) NOT NULL,
    severity_index NUMERIC(6,2) NOT NULL,
    yoy_change_pct NUMERIC(7,2) NOT NULL,
    UNIQUE (state, year, crime_category)
);

CREATE TABLE IF NOT EXISTS crime_city_year (
    id SERIAL PRIMARY KEY,
    state VARCHAR(80) NOT NULL,
    city VARCHAR(80) NOT NULL,
    year INT NOT NULL,
    cases_reported INT NOT NULL,
    crime_rate_per_100k NUMERIC(10,2) NOT NULL,
    detection_rate NUMERIC(6,2) NOT NULL,
    women_helpdesk_coverage NUMERIC(6,2) NOT NULL,
    cyber_crime_share NUMERIC(6,2) NOT NULL,
    severity_index NUMERIC(6,2) NOT NULL,
    UNIQUE (state, city, year)
);

CREATE INDEX idx_crime_state_year ON crime_state_year(year, state);
CREATE INDEX idx_crime_state_category ON crime_state_year(crime_category, state);
CREATE INDEX idx_crime_city_year ON crime_city_year(year, state, city);
