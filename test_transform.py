from etl.extract.weather_api import OpenMeteoClient
from etl.transform.weather_transformer import WeatherTransformer

client = OpenMeteoClient()
transformer = WeatherTransformer()

df = client.get_current_weather(
    latitude=-12.0464,
    longitude=-77.0428
)

df = transformer.transform(df)

print(df)

print(df.dtypes)