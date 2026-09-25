# Retail Customer 360 AI Pipeline

Pipeline end-to-end de Data Engineering y Machine Learning para construir una vista 360° de clientes a partir de información de clientes, ventas y productos.

El proyecto implementa una solución local reproducible que integra fuentes de datos, almacenamiento RAW, procesamiento, calidad, modelado con dbt, orquestación con Apache Airflow, feature engineering, Machine Learning, tracking con MLflow y una API de predicción con FastAPI.

---

## 1. Objetivo

Construir una plataforma de datos para un escenario Retail / E-commerce que permita:

- Integrar información proveniente de diferentes fuentes.
- Conservar los datos originales en una capa RAW.
- Limpiar y estandarizar los datos.
- Aplicar reglas explícitas de calidad.
- Detener el flujo ante fallos de calidad bloqueantes.
- Modelar los datos mediante capas de staging, intermediate y mart.
- Construir un dataset de features a nivel cliente.
- Entrenar un modelo de clasificación para identificar clientes en riesgo.
- Registrar información del entrenamiento mediante MLflow.
- Exponer predicciones mediante una API REST.

La pregunta de negocio utilizada es:

> ¿Qué clientes presentan mayor probabilidad de dejar de comprar?

---

## 2. Arquitectura

La arquitectura completa se encuentra en:

```text
architecture/architecture.png
```

Flujo lógico:

```text
                    FUENTES DE DATOS
                           |
              +------------+------------+
              |                         |
       Clientes / Ventas          Productos
       Datos sintéticos           DummyJSON API
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
             +-------------+-------------+
             |             |             |
          STAGING     INTERMEDIATE      MART
             |             |             |
             |      int_sales_enriched  |
             |                           |
             +---------------------------+
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

Apache Airflow orquesta el flujo completo.

---

## 3. Fuentes de datos

El proyecto utiliza dos tipos de fuente.

### 3.1 Clientes

Datos sintéticos generados localmente.

Archivo:

```text
customers.csv
```

Campos principales:

```text
customer_id
signup_date
city
segment
```

### 3.2 Ventas

Datos sintéticos generados localmente.

Archivo:

```text
sales.csv
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

Fuente externa REST:

```text
DummyJSON Products API
```

Los datos originales se almacenan en RAW antes de ser procesados.

---

## 4. Estructura del proyecto

```text
IA_pipeline/
│
├── README.md
├── .gitignore
├── docker-compose.yml
├── pytest.ini
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
│       └── retail_customer_360.py
│
├── ml/
│   ├── train_model.py
│   ├── train_model_mlflow.py
│   └── reports/
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
| Storage RAW | Filesystem |
| Base de datos | PostgreSQL |
| Transformaciones | dbt Core |
| Orquestación | Apache Airflow 3 |
| Machine Learning | scikit-learn |
| Tracking | MLflow |
| API | FastAPI |
| Contenedores | Docker Compose |
| Control de versiones | Git / GitHub |

La solución utiliza tecnologías locales para evitar dependencia de servicios cloud y facilitar la reproducibilidad del proyecto.

---

## 6. Requisitos

Se requiere:

- Windows, Linux o macOS.
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

---

## 7. Configuración

Las credenciales y variables de entorno se mantienen fuera del repositorio mediante `.env`.

Ejemplo conceptual:

```text
POSTGRES_DB=retaildb
POSTGRES_USER=retail_user
POSTGRES_PASSWORD=********
DB_HOST=postgres
```

El archivo `.env` no debe subirse al repositorio.

---

## 8. Ejecución con Docker

Desde la raíz del proyecto:

```powershell
docker compose up -d --build
```

Comprobar los contenedores:

```powershell
docker compose ps
```

Los principales servicios utilizados son:

```text
PostgreSQL
Apache Airflow
pgAdmin
```

---

## 9. Airflow

Airflow ejecuta y orquesta el pipeline.

DAG principal:

```text
retail_customer_360
```

El flujo incluye:

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
process_sales
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

La ejecución del DAG puede realizarse desde la interfaz de Airflow.

---

## 10. RAW

Los datos originales se almacenan antes del procesamiento.

Estructura:

```text
raw/
├── customers/
├── sales/
└── products/
```

Los productos obtenidos desde la API REST se almacenan conservando el archivo original y una marca temporal.

La capa RAW permite mantener trazabilidad del origen de los datos.

---

## 11. Procesamiento

Los datos son limpiados y estandarizados antes de ingresar a PostgreSQL.

Estructura:

```text
processing/
├── customers/
│   └── customers_clean.csv
├── sales/
│   └── sales_clean.csv
└── products/
    └── products_clean.csv
```

---

## 12. Calidad de datos

Las validaciones se encuentran en:

```text
quality/quality_checks.py
```

Entre las reglas implementadas:

- `customer_id` no nulo.
- `customer_id` único.
- `product_id` no nulo.
- `product_id` único.
- `sale_id` único.
- `quantity > 0`.
- `unit_price >= 0`.
- Fechas válidas.
- Existencia de clientes referenciados.
- Existencia de productos referenciados.
- Consistencia de `total_line`.

Las reglas críticas son bloqueantes.

Si una regla bloqueante falla, el proceso termina con error y no continúa hacia las siguientes etapas.

El resultado de las validaciones se conserva en:

```text
quality/reports/quality_report.json
```

---

## 13. PostgreSQL

PostgreSQL almacena las diferentes capas de datos.

### Staging

```text
retail_staging.customers
retail_staging.sales
retail_staging.products
```

### Mart

```text
retail_mart.customer_features
```

La transformación analítica principal se construye mediante dbt.

---

## 14. dbt

El proyecto utiliza dbt Core para implementar las transformaciones SQL.

Estructura:

```text
dbt/
├── dbt_project.yml
├── profiles.yml
└── models/
    ├── staging/
    │   ├── stg_customers.sql
    │   ├── stg_sales.sql
    │   ├── stg_products.sql
    │   └── schema.yml
    │
    ├── intermediate/
    │   └── int_sales_enriched.sql
    │
    └── marts/
        ├── customer_360.sql
        └── schema.yml
```

### Staging

Normaliza y expone las tablas de origen.

Modelos:

```text
stg_customers
stg_sales
stg_products
```

### Intermediate

Enriquece las ventas con información de clientes y productos.

Modelo:

```text
int_sales_enriched
```

Incluye el cálculo:

```text
total_line = quantity * unit_price
```

### Mart

Construye la vista 360° del cliente.

Modelo:

```text
customer_360
```

Incluye métricas como:

```text
total_purchases
total_quantity
total_spent
average_ticket
last_purchase_date
unique_products
```

---

## 15. Tests de dbt

Se implementan tests para verificar:

- `not_null`
- `unique`
- `relationships`

Ejemplo:

```text
customer_id
sale_id
product_id
```

Los tests se ejecutan mediante:

```powershell
dbt test
```

La construcción completa puede ejecutarse mediante:

```powershell
dbt build
```

---

## 16. Feature Engineering

Las features se construyen mediante:

```text
database/build_features.py
```

El dataset final se almacena en:

```text
retail_mart.customer_features
```

Las principales variables utilizadas son:

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

---

## 17. Variable objetivo

Se define:

```text
at_risk = 1
```

cuando:

```text
recency_days > 30
```

En caso contrario:

```text
at_risk = 0
```

La fecha de referencia corresponde a la fecha máxima de última compra disponible en el dataset.

---

## 18. Machine Learning

Se utiliza un modelo de clasificación basado en:

```text
LogisticRegression
```

El pipeline de Machine Learning incluye:

```text
StandardScaler
OneHotEncoder
LogisticRegression
```

Las variables utilizadas por el modelo son:

```text
city
segment
total_purchases
total_quantity
total_spent
average_ticket
unique_products
```

El dataset se divide en entrenamiento y prueba.

---

## 19. Métricas

El modelo registra métricas de evaluación como:

```text
accuracy
precision
recall
f1
```

Los resultados se almacenan en:

```text
ml/reports/metrics.json
```

El modelo generado localmente se mantiene fuera del repositorio mediante `.gitignore`.

---

## 20. MLflow

MLflow se utiliza para registrar los experimentos de Machine Learning.

Se registra información como:

- run_id
- dataset utilizado
- features
- algoritmo
- hiperparámetros
- métricas
- modelo
- información del experimento

Experimento:

```text
customer_risk_prediction
```

MLflow permite mantener trazabilidad de los entrenamientos y facilitar la reproducibilidad.

---

## 21. FastAPI

FastAPI proporciona la salida consumible del proyecto.

Iniciar la API localmente:

```powershell
uvicorn api.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

Documentación OpenAPI:

```text
http://127.0.0.1:8000/docs
```

### Health check

```text
GET /health
```

### Predicción

```text
GET /predict/{customer_id}
```

Ejemplo:

```text
GET /predict/C0001
```

Respuesta:

```json
{
  "customer_id": "C0001",
  "at_risk": 1,
  "prediction": "Cliente en riesgo",
  "risk_probability": 0.79
}
```

Si el cliente no existe, la API devuelve un error HTTP 404.

---

## 22. Tests

Los tests de la API se encuentran en:

```text
tests/api/test_main.py
```

Ejecutar:

```powershell
pytest tests\api\test_main.py -v
```

---

## 23. Ejecución manual de las etapas

Aunque Airflow es el orquestador principal, las etapas pueden ejecutarse individualmente para desarrollo y pruebas.

### Generar datos

```powershell
python ingestion/generate_synthetic_data.py
```

### Ingestar productos

```powershell
python ingestion/products/products_ingestion.py
```

### Procesar datos

```powershell
python processing/customers/customers_processing.py
python processing/sales/sales_processing.py
python processing/products/products_processing.py
```

### Ejecutar calidad

```powershell
python quality/quality_checks.py
```

### Inicializar base de datos

```powershell
python database/init_retail_db.py
```

### Cargar staging

```powershell
python database/load_staging.py
```

### Construir features

```powershell
python database/build_features.py
```

### Entrenar con MLflow

```powershell
python ml/train_model_mlflow.py
```

---

## 24. Flujo end-to-end

El flujo completo es:

```text
1. Generación de clientes y ventas
        ↓
2. Ingesta de productos desde REST API
        ↓
3. Almacenamiento RAW
        ↓
4. Procesamiento y estandarización
        ↓
5. Validaciones de calidad
        ↓
6. PostgreSQL / staging
        ↓
7. Transformaciones dbt
        ↓
8. customer_360
        ↓
9. Feature Engineering
        ↓
10. customer_features
        ↓
11. Entrenamiento del modelo
        ↓
12. Tracking con MLflow
        ↓
13. Predicción mediante FastAPI
```

Apache Airflow orquesta las dependencias entre las etapas.

---

## 25. Trazabilidad

El proyecto conserva trazabilidad en diferentes niveles:

### Datos

Los archivos originales se conservan en RAW.

### Calidad

Las validaciones generan:

```text
quality/reports/quality_report.json
```

### Transformaciones

dbt permite identificar los modelos utilizados:

```text
staging
intermediate
marts
```

### Machine Learning

MLflow registra:

```text
run_id
dataset
features
algoritmo
hiperparámetros
métricas
modelo
```

Esto permite relacionar los datos utilizados con el entrenamiento y el modelo generado.

---

## 26. Gobierno y seguridad

Los detalles de gobierno se encuentran en:

```text
docs/governance.md
```

Las decisiones tecnológicas se documentan en:

```text
docs/decisions.md
```

El diccionario de datos se encuentra en:

```text
docs/data_dictionary.md
```

No se deben almacenar credenciales, tokens o archivos `.env` en el repositorio.

---

## 27. Documentación

```text
docs/
├── decisions.md
├── data_dictionary.md
└── governance.md
```

### decisions.md

Documenta las principales decisiones técnicas, alternativas, motivos, trade-offs y posibles cambios para producción.

### data_dictionary.md

Describe las entidades, campos, capas, relaciones, features y elementos principales del proyecto.

### governance.md

Documenta aspectos de calidad, trazabilidad, seguridad, acceso, retención, cambios y consideraciones de producción.

---

## 28. Arquitectura de producción

El proyecto está diseñado como una implementación local y académica.

Para un escenario productivo podrían sustituirse componentes por servicios administrados equivalentes, por ejemplo:

```text
Filesystem       → Object Storage
PostgreSQL       → Data Warehouse
Airflow local    → Airflow administrado
MLflow local     → ML platform administrada
FastAPI local    → Servicio API administrado
```

Las decisiones y alternativas se encuentran documentadas en:

```text
docs/decisions.md
```

---

## 29. Estado del proyecto

El pipeline implementa:

- Ingesta de múltiples fuentes.
- RAW con trazabilidad.
- Procesamiento y estandarización.
- Reglas de calidad.
- Reglas bloqueantes.
- PostgreSQL.
- Modelado con dbt.
- Tests de dbt.
- Orquestación con Airflow.
- Feature Engineering.
- Machine Learning.
- Tracking con MLflow.
- API REST con FastAPI.
- Tests automatizados.
- Documentación técnica.
- Ejecución mediante Docker.

---

## 30. Autor

Proyecto final — AI Data Engineer

Retail Customer 360