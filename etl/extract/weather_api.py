import requests
import pandas as pd


class OpenMeteoClient:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> pd.DataFrame:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "pressure_msl",
                "wind_speed_10m",
                "wind_direction_10m",
                "cloud_cover"
            ]
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        weather = response.json()["current"]

        df = pd.DataFrame([weather])

        return df