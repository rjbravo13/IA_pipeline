import pandas as pd

from config.database import engine


class WeatherLoader:

    TABLE_NAME = "weather_data"

    def load(self, df: pd.DataFrame) -> None:

        df.to_sql(
            name=self.TABLE_NAME,
            con=engine,
            if_exists="append",
            index=False
        )

        print(f"Se insertaron {len(df)} registros.")