from etl.extract.weather_api import OpenMeteoClient

client = OpenMeteoClient()

df = client.get_current_weather(
    latitude=-12.0464,
    longitude=-77.0428
)

print(df)