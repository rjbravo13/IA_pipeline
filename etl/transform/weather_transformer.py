import pandas as pd


class WeatherTransformer:

    COLUMN_MAPPING = {
        "time": "observation_time",
        "temperature_2m": "temperature",
        "relative_humidity_2m": "humidity",
        "apparent_temperature": "apparent_temperature",
        "precipitation": "precipitation",
        "pressure_msl": "pressure",
        "wind_speed_10m": "wind_speed",
        "wind_direction_10m": "wind_direction",
        "cloud_cover": "cloud_cover"
    }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.rename(columns=self.COLUMN_MAPPING)

        df["observation_time"] = pd.to_datetime(df["observation_time"])

        # Eliminar columnas que no almacenaremos
        df = df.drop(columns=["interval"], errors="ignore")

        return df