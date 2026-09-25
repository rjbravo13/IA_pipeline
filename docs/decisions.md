# Decisiones tecnológicas

## 1. Almacenamiento de datos RAW

### Elegido
Filesystem local.

### Alternativa
MinIO.

### Justificación
Se eligió Filesystem local porque el proyecto se ejecuta en un entorno local y académico, y permite conservar los archivos originales de las fuentes con trazabilidad y marca temporal.

La estructura RAW permite conservar los datos originales antes de las transformaciones.

### Cambio esperado en producción
En un entorno productivo se podría reemplazar el almacenamiento local por un object storage como S3, Azure Blob Storage o MinIO.

---

## 2. Base de datos

### Elegido
PostgreSQL.

### Alternativa
DuckDB.

### Justificación
PostgreSQL permite representar las diferentes capas del modelo de datos, aplicar relaciones entre entidades y servir los datos procesados a otros componentes del proyecto.

También facilita la integración con dbt, Airflow y la API.

### Cambio esperado en producción
La solución podría mantenerse en PostgreSQL administrado o migrarse a una plataforma de datos administrada dependiendo del volumen, disponibilidad y necesidades de escalabilidad.

---

## 3. Procesamiento

### Elegido
Python y Pandas.

### Alternativa
PySpark.

### Justificación
Pandas resulta suficiente para el volumen de datos utilizado en este proyecto y permite implementar de forma sencilla la limpieza, transformación y validación de los datos.

### Cambio esperado en producción
Para volúmenes significativamente mayores se podría utilizar PySpark o un motor distribuido equivalente.

---

## 4. Transformaciones y modelado

### Elegido
dbt Core.

### Alternativa
Transformaciones exclusivamente mediante scripts Python/SQL.

### Justificación
dbt permite organizar las transformaciones en modelos por capas y ejecutar pruebas de calidad sobre los modelos.

El proyecto utiliza modelos de:

- staging
- intermediate
- marts

Además, se utilizan pruebas como `not_null`, `unique` y `relationships`.

### Cambio esperado en producción
Se podría utilizar dbt en un entorno administrado o integrarlo con una plataforma de datos empresarial.

---

## 5. Orquestación

### Elegido
Apache Airflow 3 ejecutado mediante Docker.

### Alternativa
Ejecución mediante cron o scripts independientes.

### Justificación
Airflow permite representar las dependencias entre las diferentes etapas del pipeline y centralizar su ejecución.

El DAG `retail_customer_360` integra:

1. generación de datos sintéticos;
2. ingesta de productos;
3. procesamiento;
4. controles de calidad;
5. carga de staging;
6. ejecución de dbt;
7. construcción de features;
8. entrenamiento del modelo.

### Cambio esperado en producción
Se podría utilizar Airflow administrado o una plataforma equivalente de orquestación.

---

## 6. Machine Learning

### Elegido
scikit-learn.

### Alternativa
PySpark ML.

### Justificación
El volumen de datos del proyecto permite utilizar scikit-learn para implementar un modelo de clasificación sencillo.

Se utiliza regresión logística con:

- StandardScaler
- OneHotEncoder
- LogisticRegression

### Cambio esperado en producción
Para mayores volúmenes de datos se podría evaluar PySpark ML u otra plataforma de machine learning distribuido.

---

## 7. Tracking de experimentos

### Elegido
MLflow.

### Alternativa
Registro manual de métricas.

### Justificación
MLflow permite registrar experimentos, parámetros, métricas y modelos, facilitando la trazabilidad y reproducibilidad del entrenamiento.

### Cambio esperado en producción
En producción se podría utilizar un backend y almacenamiento de artefactos administrados y con alta disponibilidad.

---

## 8. API de consumo

### Elegido
FastAPI.

### Alternativa
Consumo directo desde PostgreSQL.

### Justificación
FastAPI permite exponer los resultados del modelo mediante una API REST y proporciona documentación interactiva mediante OpenAPI.

El endpoint de predicción permite consultar el riesgo de un cliente mediante su `customer_id`.

### Cambio esperado en producción
La API podría desplegarse detrás de un gateway, con autenticación, autorización, observabilidad y escalabilidad horizontal.

---

## 9. Contenedores

### Elegido
Docker Compose.

### Alternativa
Ejecución directa de todos los componentes en el sistema operativo.

### Justificación
Docker Compose permite ejecutar PostgreSQL, Airflow y otros componentes de infraestructura de forma reproducible en el entorno local.

### Cambio esperado en producción
Los servicios podrían desplegarse mediante Kubernetes u otra plataforma de contenedores administrada.

---

## 10. Fuente REST

### Elegido
DummyJSON Products API.

### Alternativa
Una API comercial o empresarial de productos.

### Justificación
DummyJSON permite disponer de una fuente REST externa para cumplir el requisito de integración con una segunda fuente de datos sin requerir credenciales.

La respuesta de la API se conserva inicialmente en RAW antes de ser procesada.

### Cambio esperado en producción
La fuente podría reemplazarse por una API empresarial con autenticación, contratos de servicio, monitoreo y controles de disponibilidad.