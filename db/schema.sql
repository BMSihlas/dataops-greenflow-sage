-- Create sensor_data table
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255),
    energy_kwh FLOAT,
    water_m3 FLOAT,
    co2_emissions FLOAT,
    sector VARCHAR(100)
);

-- Create insights table
CREATE TABLE IF NOT EXISTS insights (
    id SERIAL PRIMARY KEY,
    sector VARCHAR(100),
    avg_energy_kwh FLOAT,
    avg_water_m3 FLOAT,
    avg_co2_emissions FLOAT
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash text NOT NULL,
    created_at BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW()),
    last_login BIGINT DEFAULT NULL
);