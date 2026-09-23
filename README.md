# Retail Customer 360 AI Pipeline

Pipeline de Data Engineering y Machine Learning para construir una vista 360° de clientes a partir de información de ventas, clientes y productos.

El proyecto implementa un flujo completo de:

- Ingesta de datos
- Almacenamiento RAW
- Procesamiento y estandarización
- Validaciones de calidad
- Modelo de datos por capas
- Orquestación con Apache Airflow
- Construcción de features de clientes
- Entrenamiento de un modelo de clasificación
- Tracking de experimentos con MLflow
- Exposición de predicciones mediante FastAPI
- Ejecución mediante Docker

---

## Objetivo

Construir una solución local de Customer 360 que permita integrar información de clientes, ventas y productos para generar características agregadas por cliente y utilizarlas en un modelo de clasificación.

El pipeline produce una tabla final de características de clientes y una predicción de riesgo.

---

## Arquitectura

`	ext
                    FUENTES
                       |
             +---------+---------+
             |                   |
       Datos sintéticos      REST API
       Clientes / Ventas       Productos
             |                   |
             +---------+---------+
                       |
                       v
                    RAW
                       |
                       v
              PROCESAMIENTO
                       |
                       v
                  QUALITY
                       |
                       v
              PostgreSQL
                       |
          +------------+------------+
          |            |            |
          v            v            v
       STAGING     INTERMEDIATE     MART
          |            |            |
          |            |       customer_360
          |            |            |
          |            +------------+
          |                         |
          +-------------------------+
                                    |
                                    v
                           customer_features
                                    |
                                    v
                                  MLflow
                                    |
                                    v
                            Modelo de riesgo
                                    |
                                    v
                                FastAPI
