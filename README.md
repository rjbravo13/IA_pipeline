# Retail Customer 360 - AI Data Engineer

## 1. Descripción del proyecto

Este proyecto implementa un pipeline de datos para construir una vista Customer 360 y desarrollar un modelo de clasificación para identificar clientes con riesgo.

La solución integra procesos de:

- Generación e ingesta de datos.
- Almacenamiento RAW.
- Procesamiento y estandarización.
- Validaciones de calidad.
- Carga en PostgreSQL.
- Transformaciones mediante dbt.
- Construcción de Customer 360.
- Feature Engineering.
- Entrenamiento de Machine Learning.
- Tracking mediante MLflow.
- Exposición de predicciones mediante FastAPI.
- Orquestación mediante Apache Airflow.
- Pruebas automatizadas.

El proyecto está diseñado para ejecutarse localmente utilizando Python y Docker.

---

## 2. Arquitectura

El flujo general de procesamiento es:

```text
Datos sintéticos          DummyJSON API
       |                         |
       +------------+------------+
                    |
                    v
                  RAW
                    |
                    v
             PROCESAMIENTO
                    |
                    v
             CALIDAD DE DATOS
                    |
                    v
               PostgreSQL
                    |
                    v
                  dbt
                    |
          +---------+---------+
          |         |         |
       STAGING  INTERMEDIATE  MART
          |         |         |
          |   int_sales_enriched
          |                   |
          +---------+---------+
                    |
                    v
              customer_360
                    |
                    v
            customer_features
                    |
                    v
            Machine Learning
              scikit-learn
                    |
                    v
                 MLflow
                    |
                    v
          Modelo de clasificación
                    |
                    v
                 FastAPI
                    |
                    v
           Predicción de riesgo
```

Apache Airflow orquesta las dependencias entre las diferentes etapas del pipeline.

---

## 3. Fuentes de datos

El proyecto utiliza diferentes fuentes de datos.

### 3.1 Clientes

Los datos de clientes son generados mediante un proceso sintético.

El archivo generado se almacena en la zona RAW utilizando una marca temporal de ingesta.

Formato:

```text
customers_YYYYMMDD_HHMMSS.csv
```

Campos principales:

```text
customer_id
signup_date
city
segment
```

### 3.2 Ventas

Los datos de ventas son generados mediante un proceso sintético.

El archivo generado se almacena en la zona RAW utilizando una marca temporal de ingesta.

Formato:

```text
sales_YYYYMMDD_HHMMSS.csv
```

Campos principales:

```text
sale_id
customer_id
product_id
timestamp
quantity
unit_price
```

### 3.3 Productos

Los productos se obtienen mediante una fuente externa REST:

```text
DummyJSON Products API
```

Los datos obtenidos desde la API se almacenan en la zona RAW antes de ser procesados.

Los archivos conservan información temporal asociada a la ingesta.

---

## 4. Estructura del proyecto

```text
IA_pipeline/
│
├── README.md
├── .gitignore
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
│
├── architecture/
│   └── architecture.png
│
├── ingestion/
│   ├── generate_synthetic_data.py
│   └── products/
│       └── products_ingestion.py
│
├── processing/
│   ├── customers/
│   ├── sales/
│   └── products/
│
├── quality/
│   ├── quality_checks.py
│   └── reports/
│       └── quality_report.json
│
├── database/
│   ├── init_retail_db.py
│   ├── load_staging.py
│   └── build_features.py
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
│
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dags/
│       └── retail_customer_360_dag.py
│
├── ml/
│   ├── train_model_mlflow.py
│   └── models/
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   └── api/
│       └── test_main.py
│
└── docs/
    ├── decisions.md
    ├── data_dictionary.md
    └── governance.md
```

---

## 5. Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python |
| Procesamiento | Pandas |
| Almacenamiento RAW | Filesystem |
| Base de datos | PostgreSQL |
| Transformaciones | dbt Core |
| Orquestación | Apache Airflow |
| Machine Learning | scikit-learn |
| Tracking | MLflow |
| API | FastAPI |
| Contenedores | Docker Compose |
| Control de versiones | Git / GitHub |

La solución utiliza tecnologías locales para facilitar la reproducibilidad del proyecto.

---

## 6. Requisitos

Se requiere:

- Python 3.11 o compatible.
- Docker Desktop.
- Git.
- VS Code recomendado para desarrollo.

Comprobar Docker:

```powershell
docker --version
docker compose version
```

Comprobar Python:

```powershell
python --version
```

Comprobar Git:

```powershell
git --version
```

---

## 7. Configuración

Las credenciales y variables de entorno se mantienen fuera del repositorio mediante el archivo `.env`.

Después de clonar el repositorio, crear el archivo `.env` a partir del archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Configurar las variables requeridas por el proyecto.

El archivo `.env` no debe subirse al repositorio.

Las credenciales reales deben mantenerse únicamente mediante variables de entorno.

---

## 8. Ejecución con Docker

Desde la raíz del proyecto ejecutar:

```powershell
docker compose up -d --build
```

Comprobar el estado de los servicios:

```powershell
docker compose ps
```

Los principales servicios utilizados son:

```text
PostgreSQL
Apache Airflow
pgAdmin
```

Para detener los servicios:

```powershell
docker compose down
```

---

## 9. Airflow

Apache Airflow se utiliza para orquestar el pipeline mediante el DAG:

```text
retail_customer_360
```

El DAG contiene las siguientes tareas principales:

```text
generate_synthetic_data
        |
        +--> process_customers
        |
        +--> process_sales

ingest_products
        |
        v
process_products

process_customers
        |
process_sales
        |
process_products
        |
        v
quality_checks
        |
        v
init_retail_db
        |
        v
load_staging
        |
        v
dbt_build
        |
        v
build_features
        |
        v
train_model_mlflow
```

Las dependencias son administradas por Airflow.

Las tareas utilizan reintentos para manejar errores transitorios:

```text
retries: 2
retry_delay: 2 minutos
```

El DAG puede ejecutarse desde la interfaz web de Airflow.

---

## 10. RAW

Los datos originales se almacenan antes de aplicar transformaciones.

La estructura de la zona RAW es:

```text
raw/
├── customers/
├── sales/
└── products/
```

Los archivos de clientes utilizan una marca temporal de ingesta:

```text
customers_YYYYMMDD_HHMMSS.csv
```

Los archivos de ventas utilizan una marca temporal de ingesta:

```text
sales_YYYYMMDD_HHMMSS.csv
```

Los productos obtenidos desde la API REST también se almacenan en RAW antes de su procesamiento.

La zona RAW permite conservar los datos originales y mantener trazabilidad sobre las diferentes ejecuciones de ingesta.

---

## 11. Procesamiento

Los datos son limpiados, tipados y estandarizados antes de ingresar a PostgreSQL.

La estructura es:

```text
processing/
├── customers/
│   └── customers_clean.csv
├── sales/
│   └── sales_clean.csv
└── products/
    └── products_clean.csv
```

Entre las operaciones realizadas se encuentran:

- Limpieza de datos.
- Conversión de tipos.
- Estandarización.
- Eliminación de duplicados.
- Validación de valores.
- Preparación de los datos para la carga en PostgreSQL.

Los procesos de clientes y ventas identifican el archivo RAW más reciente mediante el patrón de nombre con timestamp.

---

## 12. Calidad de datos

Las validaciones de calidad se implementan mediante:

```text
quality/quality_checks.py
```

El resultado se genera en:

```text
quality/reports/quality_report.json
```

Las reglas implementadas incluyen validaciones de:

- Completitud.
- Unicidad.
- Validez.
- Integridad referencial.
- Consistencia.
- Valores permitidos.
- Consistencia de cálculos.

El proceso contiene reglas bloqueantes.

Cuando una regla bloqueante falla, el pipeline se detiene mediante una excepción:

```text
RuntimeError("Proceso detenido por fallos de calidad.")
```

Esto evita que datos que no cumplen las reglas definidas continúen hacia las siguientes etapas.

---

## 13. PostgreSQL

PostgreSQL se utiliza como base de datos principal para almacenar los datos procesados y las diferentes capas del modelo de datos.

La inicialización de la base de datos se realiza mediante:

```text
database/init_retail_db.py
```

La carga de los datos procesados hacia staging se realiza mediante:

```text
database/load_staging.py
```

Las tablas de staging reciben los datos antes de las transformaciones realizadas mediante dbt.

---

## 14. dbt

dbt Core se utiliza para realizar las transformaciones y el modelado de datos.

La estructura de modelos es:

```text
dbt/
└── models/
    ├── staging/
    │   ├── stg_customers.sql
    │   ├── stg_products.sql
    │   ├── stg_sales.sql
    │   └── schema.yml
    │
    ├── intermediate/
    │   └── int_sales_enriched.sql
    │
    └── marts/
        ├── customer_360.sql
        └── schema.yml
```

Las capas utilizadas son:

```text
staging
intermediate
marts
```

Los modelos incluyen pruebas de dbt como:

```text
not_null
unique
relationships
```

Estas pruebas permiten validar la estructura y consistencia de los modelos generados.

---

## 15. Customer 360

El modelo principal de negocio es:

```text
customer_360
```

Este modelo consolida información relacionada con los clientes y sus compras.

La información consolidada se utiliza posteriormente para construir el conjunto de características utilizado por Machine Learning.

---

## 16. Feature Engineering

A partir de la información consolidada se construye el dataset de características a nivel de cliente.

Las principales características utilizadas son:

```text
customer_id
city
segment
total_purchases
total_quantity
total_spent
average_ticket
unique_products
recency_days
at_risk
```

El dataset de features se construye a nivel de cliente.

La variable objetivo utilizada para el modelo es:

```text
at_risk
```

---

## 17. Machine Learning

El proyecto utiliza `scikit-learn` para construir un modelo de clasificación de riesgo de clientes.

El pipeline de Machine Learning utiliza:

```text
OneHotEncoder
StandardScaler
LogisticRegression
```

La separación de los datos se realiza mediante:

```text
Train: 80%
Test: 20%
random_state: 42
stratify: target
```

El modelo se evalúa utilizando:

```text
accuracy
precision
recall
f1
```

El modelo entrenado se almacena en:

```text
ml/models/customer_risk_model_mlflow.joblib
```

---

## 18. MLflow

MLflow se utiliza para registrar los experimentos y mantener la trazabilidad de los entrenamientos de Machine Learning.

Para cada ejecución se registra información como:

```text
run_id
training_timestamp
dataset_version
feature_columns
algoritmo
hiperparámetros
métricas
model_version
```

La versión del modelo se relaciona con el `run_id` de MLflow, permitiendo identificar la ejecución que generó el modelo.

Adicionalmente, se genera un archivo de metadata asociado al modelo:

```text
ml/models/customer_risk_model_mlflow_metadata.json
```

Este archivo contiene información de trazabilidad:

```text
run_id
model_version
training_timestamp
dataset_version
feature_columns
target
```

Esto permite relacionar el dataset utilizado, las features, el entrenamiento y el modelo generado.

---

## 19. Resultados del modelo

En una ejecución de entrenamiento se obtuvieron los siguientes resultados sobre el conjunto de prueba:

```text
Accuracy  : 0.5500
Precision : 0.5833
Recall    : 0.6364
F1        : 0.6087
```

Estos valores corresponden a una ejecución específica del modelo y pueden cambiar cuando se utilice un dataset diferente o se modifique el proceso de entrenamiento.

---

## 20. FastAPI

FastAPI se utiliza para exponer el modelo mediante una API REST.

La aplicación se encuentra en:

```text
api/main.py
```

Para iniciar la API localmente:

```powershell
uvicorn api.main:app --reload --env-file .env
```

La documentación interactiva está disponible en:

```text
http://127.0.0.1:8000/docs
```

El endpoint principal de predicción es:

```text
GET /predict/{customer_id}
```

Ejemplo:

```text
GET /predict/C0001
```

La API devuelve la predicción y la información de trazabilidad correspondiente.

Ejemplo:

```json
{
  "customer_id": "C0001",
  "at_risk": 1,
  "prediction": "Cliente en riesgo",
  "risk_probability": 0.7929,
  "prediction_timestamp": "2026-10-02T22:09:37.333403+00:00",
  "model_version": "8e63d3306cd34bcab8d08e77c83fb2e5",
  "run_id": "8e63d3306cd34bcab8d08e77c83fb2e5"
}
```

La respuesta contiene:

```text
customer_id
at_risk
prediction
risk_probability
prediction_timestamp
model_version
run_id
```

El campo `prediction_timestamp` identifica cuándo se generó la predicción.

Los campos `model_version` y `run_id` permiten relacionar la predicción con la ejecución de entrenamiento correspondiente.

---

## 21. Health Check

La API dispone de un endpoint para verificar el estado del servicio:

```text
GET /health
```

El endpoint permite comprobar si el modelo se encuentra cargado correctamente.

Ejemplo conceptual de respuesta:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

## 22. Trazabilidad

El proyecto implementa trazabilidad en diferentes niveles.

### Datos RAW

Los archivos originales se conservan en la zona RAW.

Los archivos de clientes y ventas utilizan timestamps:

```text
YYYYMMDD_HHMMSS
```

Esto permite diferenciar las diferentes ejecuciones de ingesta.

### Calidad

Los resultados de las validaciones se almacenan en:

```text
quality/reports/quality_report.json
```

### Transformaciones

dbt organiza las transformaciones en:

```text
staging
intermediate
marts
```

### Machine Learning

MLflow registra:

```text
run_id
training_timestamp
dataset_version
feature_columns
algoritmo
hiperparámetros
métricas
model_version
```

### Modelo

El modelo se guarda junto con un archivo de metadata:

```text
ml/models/customer_risk_model_mlflow.joblib
ml/models/customer_risk_model_mlflow_metadata.json
```

### Predicciones

La API incorpora:

```text
prediction_timestamp
model_version
run_id
```

Esto permite relacionar una predicción con el modelo utilizado y con la ejecución que generó dicho modelo.

---

## 23. Pruebas

Las pruebas automatizadas se encuentran en:

```text
tests/
```

Las pruebas de la API se encuentran en:

```text
tests/api/test_main.py
```

Para ejecutar las pruebas:

```powershell
pytest -q
```

Las pruebas deben ejecutarse con el entorno configurado y con los servicios requeridos disponibles.

---

## 24. Ejecución manual del pipeline

Los diferentes componentes pueden ejecutarse individualmente.

### Generación de datos

```powershell
python ingestion/generate_synthetic_data.py
```

### Ingesta de productos

```powershell
python ingestion/products/products_ingestion.py
```

### Procesamiento de clientes

```powershell
python processing/customers/customers_processing.py
```

### Procesamiento de ventas

```powershell
python processing/sales/sales_processing.py
```

### Procesamiento de productos

```powershell
python processing/products/products_processing.py
```

### Validaciones de calidad

```powershell
python quality/quality_checks.py
```

### Inicialización de PostgreSQL

```powershell
python database/init_retail_db.py
```

### Carga de staging

```powershell
python database/load_staging.py
```

### Construcción de features

```powershell
python database/build_features.py
```

### Entrenamiento del modelo

```powershell
python ml/train_model_mlflow.py
```

### Inicio de FastAPI

```powershell
uvicorn api.main:app --reload --env-file .env
```

La ejecución mediante Airflow permite ejecutar el flujo respetando las dependencias entre las diferentes etapas.

---

## 25. Ejecución completa

La secuencia general de ejecución es:

```text
1. Configurar las variables de entorno.
2. Levantar los servicios Docker.
3. Generar los datos sintéticos.
4. Obtener los productos desde la API REST.
5. Almacenar los datos originales en RAW.
6. Procesar y estandarizar los datos.
7. Ejecutar las validaciones de calidad.
8. Inicializar PostgreSQL.
9. Cargar los datos a staging.
10. Ejecutar las transformaciones dbt.
11. Construir Customer 360.
12. Construir el dataset de features.
13. Entrenar el modelo.
14. Registrar el entrenamiento en MLflow.
15. Levantar la API.
16. Ejecutar una predicción.
```

Cuando se utiliza Airflow, estas dependencias son gestionadas por el DAG:

```text
retail_customer_360
```

---

## 26. Ejecución del DAG

Para comprobar que Airflow reconoce el DAG:

```powershell
docker compose exec airflow-scheduler airflow dags list
```

Para comprobar la definición local del DAG:

```powershell
docker compose exec airflow-scheduler airflow dags list --local --output json
```

El DAG utilizado por el proyecto es:

```text
retail_customer_360
```

El archivo se encuentra en:

```text
airflow/dags/retail_customer_360_dag.py
```

---

## 27. Gobierno y seguridad

Los aspectos relacionados con gobierno y seguridad se documentan en:

```text
docs/governance.md
```

Las principales decisiones técnicas se documentan en:

```text
docs/decisions.md
```

El diccionario de datos se encuentra en:

```text
docs/data_dictionary.md
```

No se deben almacenar credenciales, tokens o archivos `.env` dentro del repositorio.

Las credenciales deben mantenerse mediante variables de entorno.

Los archivos temporales, entornos virtuales, logs y artefactos generados localmente deben mantenerse fuera del control de versiones cuando corresponda.

---

## 28. Documentación técnica

La documentación adicional se encuentra en:

```text
docs/
├── decisions.md
├── data_dictionary.md
└── governance.md
```

### decisions.md

Documenta las principales decisiones técnicas del proyecto.

Cada decisión incluye:

- Decisión.
- Alternativas consideradas.
- Motivo.
- Trade-offs.
- Cambio futuro.

### data_dictionary.md

Documenta las principales entidades y campos utilizados por el proyecto.

### governance.md

Documenta aspectos relacionados con calidad, trazabilidad, seguridad, acceso, retención y consideraciones de gobierno de datos.

---

## 29. Arquitectura para producción

El proyecto está diseñado como una implementación local.

En un escenario productivo, los componentes locales podrían sustituirse por servicios administrados equivalentes.

Por ejemplo:

```text
Filesystem
    ->
Object Storage

PostgreSQL
    ->
Base de datos o Data Warehouse administrado

Airflow local
    ->
Airflow administrado

MLflow local
    ->
Plataforma MLOps administrada

FastAPI local
    ->
Servicio API administrado
```

Estas posibles evoluciones se documentan en:

```text
docs/decisions.md
```

---

## 30. Consideraciones

El pipeline debe ejecutarse respetando las dependencias entre las diferentes etapas.

Los datos deben pasar por las validaciones de calidad antes de continuar hacia las siguientes etapas.

Las credenciales no deben almacenarse en el código fuente.

Los datos RAW deben conservarse antes de aplicar transformaciones.

Los modelos de Machine Learning deben estar asociados a información que permita identificar el entrenamiento y dataset utilizado.

Las predicciones generadas por la API incluyen información de trazabilidad para identificar el modelo utilizado.

---

## 31. Estado del proyecto

El proyecto implementa:

- Ingesta de múltiples fuentes.
- Fuente externa REST.
- Zona RAW.
- Trazabilidad de ingesta.
- Procesamiento de datos.
- Limpieza y estandarización.
- Eliminación de duplicados.
- Validaciones de calidad.
- Reglas bloqueantes.
- PostgreSQL.
- Modelado mediante dbt.
- Tests de dbt.
- Orquestación mediante Airflow.
- Reintentos de tareas.
- Feature Engineering.
- Dataset de características a nivel de cliente.
- Modelo de clasificación.
- Evaluación del modelo.
- Tracking mediante MLflow.
- Trazabilidad del entrenamiento.
- Trazabilidad de las predicciones.
- API REST mediante FastAPI.
- Pruebas automatizadas.
- Documentación técnica.
- Ejecución mediante Docker.

---

## 32. Autor

Rafael Bravo