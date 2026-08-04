CREATE TABLE weather_data (

    id SERIAL PRIMARY KEY,

    city VARCHAR(100),

    latitude NUMERIC(8,5),

    longitude NUMERIC(8,5),

    observation_time TIMESTAMP,

    temperature NUMERIC(5,2),

    humidity NUMERIC(5,2),

    apparent_temperature NUMERIC(5,2),

    precipitation NUMERIC(5,2),

    pressure NUMERIC(7,2),

    wind_speed NUMERIC(5,2),

    wind_direction NUMERIC(5,2),

    cloud_cover NUMERIC(5,2),

    created_at TIMESTAMP DEFAULT NOW()

);

CREATE TABLE etl_log (

    id SERIAL PRIMARY KEY,

    process_name VARCHAR(100),

    start_time TIMESTAMP,

    end_time TIMESTAMP,

    records_processed INTEGER,

    records_failed INTEGER,

    status VARCHAR(20),

    error_message TEXT

);