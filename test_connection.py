from sqlalchemy import text

from config.database import engine

try:

    with engine.connect() as connection:

        version = connection.execute(
            text("SELECT version();")
        ).scalar()

        print("\n========================")
        print("CONEXIÓN EXITOSA")
        print("========================")
        print(version)

except Exception as e:

    print("\n========================")
    print("ERROR")
    print("========================")
    print(e)