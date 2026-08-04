from etl.extract.weather_api import OpenMeteoClient
from etl.transform.weather_transformer import WeatherTransformer
from etl.load.weather_loader import WeatherLoader


def main():

    client = OpenMeteoClient()

    transformer = WeatherTransformer()

    loader = WeatherLoader()

    # Lima
    df = client.get_current_weather(
        latitude=-12.0464,
        longitude=-77.0428
    )

    print("\nDatos extraídos:")
    print(df)

    df = transformer.transform(df)

    print("\nDatos transformados:")
    print(df)

    loader.load(df)


if __name__ == "__main__":
    main()