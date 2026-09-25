# Diccionario de datos

## 1. Objetivo

Este documento describe las principales fuentes de datos, tablas, modelos y campos utilizados en el pipeline Retail Customer 360.

El proyecto utiliza información de clientes, ventas y productos para construir una vista consolidada del comportamiento de cada cliente y generar variables para un modelo de clasificación.

---

## 2. Fuente de clientes

### Archivo

`raw/customers/customers.csv`

### Tabla de staging

`retail_staging.customers`

### Descripción

Contiene la información básica de los clientes utilizada para construir el Customer 360.

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `customer_id` | string | Identificador único del cliente |
| `signup_date` | date | Fecha de registro del cliente |
| `city` | string | Ciudad del cliente |
| `segment` | string | Segmento comercial del cliente |

### Reglas principales

- `customer_id` no debe ser nulo.
- `customer_id` debe ser único.
- `signup_date` debe contener una fecha válida.

---

## 3. Fuente de ventas

### Archivo

`raw/sales/sales.csv`

### Tabla de staging

`retail_staging.sales`

### Descripción

Contiene las transacciones realizadas por los clientes.

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `sale_id` | string | Identificador único de la venta |
| `customer_id` | string | Identificador del cliente que realizó la compra |
| `product_id` | string | Identificador del producto vendido |
| `timestamp` | timestamp | Fecha y hora de la venta |
| `quantity` | numeric | Cantidad de unidades vendidas |
| `unit_price` | numeric | Precio unitario del producto |

### Reglas principales

- `sale_id` debe ser único.
- `customer_id` no debe ser nulo.
- `product_id` no debe ser nulo.
- `quantity` debe ser mayor que cero.
- `unit_price` debe ser mayor o igual a cero.
- `timestamp` debe contener una fecha válida.

---

## 4. Fuente de productos

### Fuente

API REST DummyJSON Products.

### Archivos RAW

Los resultados de la API se almacenan en:

`raw/products/products_YYYYMMDD_HHMMSS.json`

### Tabla de staging

`retail_staging.products`

### Descripción

Contiene información de los productos obtenida desde una fuente REST externa.

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `product_id` | string | Identificador único del producto |
| `category` | string | Categoría del producto |
| `brand` | string | Marca del producto |
| `description` | string | Descripción del producto |
| `price` | numeric | Precio del producto |

### Reglas principales

- `product_id` no debe ser nulo.
- `product_id` debe ser único.
- `price` debe contener un valor válido.

---

## 5. Capa RAW

La capa RAW conserva los datos originales obtenidos desde las fuentes antes de aplicar transformaciones.

La estructura utilizada es:

```text
raw/
├── customers/
│   └── customers.csv
├── sales/
│   └── sales.csv
└── products/
    └── products_YYYYMMDD_HHMMSS.json
```

Los archivos de productos incorporan una marca temporal en su nombre para permitir identificar diferentes ejecuciones de ingesta.

La capa RAW se utiliza como referencia para mantener trazabilidad sobre los datos originales.

---

## 6. Capa de procesamiento

Los datos RAW son transformados y limpiados antes de cargarse en PostgreSQL.

### Clientes

`processing/customers/customers_clean.csv`

### Ventas

`processing/sales/sales_clean.csv`

### Productos

`processing/products/products_clean.csv`

Esta capa prepara los datos para los controles de calidad y la carga a la base de datos.

---

## 7. Capa de staging

La capa staging contiene los datos preparados para las transformaciones posteriores.

### Schema

`retail_staging`

### Tablas

```text
retail_staging.customers
retail_staging.sales
retail_staging.products
```

Estas tablas constituyen la entrada de los modelos dbt de staging.

---

## 8. Modelos dbt

Los modelos dbt están organizados en tres niveles:

```text
dbt/models/
├── staging/
├── intermediate/
└── marts/
```

---

## 8.1 Staging

Los modelos de staging se encuentran en:

`dbt/models/staging/`

### Modelos

```text
stg_customers
stg_sales
stg_products
```

### Propósito

Los modelos de staging proporcionan una representación estructurada de las tablas de la capa `retail_staging`.

También se aplican pruebas de calidad sobre los modelos mediante dbt.

---

## 8.2 Intermediate

### Modelo

`int_sales_enriched`

### Propósito

El modelo `int_sales_enriched` combina información de ventas, clientes y productos.

Las relaciones principales utilizadas son:

```text
sales.customer_id → customers.customer_id
sales.product_id  → products.product_id
```

El modelo también calcula el importe de cada línea de venta:

```text
total_line = quantity * unit_price
```

Este modelo sirve como base para las agregaciones posteriores.

---

## 8.3 Mart

### Modelo

`customer_360`

### Propósito

El modelo `customer_360` consolida la información de cada cliente y sus compras.

El resultado contiene una fila por cliente.

### Campos

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `customer_id` | string | Identificador del cliente |
| `city` | string | Ciudad del cliente |
| `segment` | string | Segmento del cliente |
| `signup_date` | date | Fecha de registro |
| `total_purchases` | numeric | Número total de compras |
| `total_quantity` | numeric | Cantidad total de unidades compradas |
| `total_spent` | numeric | Importe total gastado |
| `average_ticket` | numeric | Ticket promedio |
| `last_purchase_date` | date | Fecha de la última compra |
| `unique_products` | numeric | Cantidad de productos diferentes comprados |

---

## 9. Features para Machine Learning

Las variables utilizadas para el modelo se encuentran en:

`retail_mart.customer_features`

Esta tabla contiene información derivada del Customer 360.

| Campo | Descripción |
|---|---|
| `customer_id` | Identificador del cliente |
| `city` | Ciudad del cliente |
| `segment` | Segmento del cliente |
| `total_purchases` | Número total de compras |
| `total_quantity` | Cantidad total comprada |
| `total_spent` | Importe total gastado |
| `average_ticket` | Ticket promedio |
| `unique_products` | Cantidad de productos diferentes comprados |
| `recency_days` | Días transcurridos desde la última compra respecto a la fecha de referencia |
| `at_risk` | Variable objetivo del modelo |

---

## 10. Variable objetivo

La variable objetivo del modelo es:

`at_risk`

Su definición se basa en `recency_days`.

La regla utilizada es:

```text
recency_days > 30  → at_risk = 1
recency_days <= 30 → at_risk = 0
```

La fecha de referencia corresponde a la fecha máxima de última compra disponible en `retail_mart.customer_360`.

En la ejecución actual del proyecto se obtuvo:

```text
at_risk = 0 → 43 clientes
at_risk = 1 → 57 clientes
```

---

## 11. Variables utilizadas por el modelo

El modelo de clasificación utiliza las siguientes variables:

```text
city
segment
total_purchases
total_quantity
total_spent
average_ticket
unique_products
```

La variable `recency_days` no se utiliza directamente como variable de entrada porque participa en la definición del objetivo `at_risk`.

---

## 12. Relaciones principales

Las principales relaciones entre las entidades son:

```text
customers
    │
    │ customer_id
    ▼
sales
    │
    │ product_id
    ▼
products
```

La relación conceptual es:

```text
customers 1 ─────── N sales N ─────── 1 products
```

A partir de estas relaciones se construyen las diferentes capas:

```text
customers ─────────┐
                   │
sales ─────────────┼──> int_sales_enriched
                   │
products ──────────┘
                         │
                         ▼
                    customer_360
                         │
                         ▼
                  customer_features
                         │
                         ▼
                  Machine Learning
```

---

## 13. Calidad de datos

El proyecto implementa controles de calidad antes de continuar con las siguientes etapas del pipeline.

Entre las validaciones implementadas se encuentran:

- Identificadores de cliente no nulos.
- Identificadores de producto no nulos.
- Cantidades mayores que cero.
- Precios unitarios mayores o iguales a cero.
- Fechas válidas.
- Unicidad de `sale_id`.
- Existencia de relaciones entre entidades.
- Consistencia del importe de línea.

Los modelos dbt también cuentan con pruebas de:

- `not_null`
- `unique`
- `relationships`

Los resultados de los controles generales de calidad se almacenan en:

`quality/reports/quality_report.json`

---

## 14. Trazabilidad

El flujo general de los datos es:

```text
Fuente
  │
  ▼
RAW
  │
  ▼
Processing
  │
  ▼
Quality
  │
  ▼
PostgreSQL Staging
  │
  ▼
dbt Staging
  │
  ▼
dbt Intermediate
  │
  ▼
dbt Mart
  │
  ▼
Customer Features
  │
  ▼
Machine Learning
  │
  ▼
API
```

Cada etapa representa una transformación o validación dentro del pipeline.

La capa RAW permite conservar los datos originales antes de las transformaciones.

Los archivos de productos incluyen una marca temporal en el nombre del archivo para facilitar la identificación de las diferentes ejecuciones de ingesta.

---

## 15. Capas principales de datos

| Capa | Propósito |
|---|---|
| RAW | Conservación de los datos originales |
| Processing | Limpieza y transformación inicial |
| Quality | Validación de reglas de calidad |
| Staging | Preparación de datos para transformación |
| Intermediate | Integración y enriquecimiento |
| Mart | Modelo analítico Customer 360 |
| Features | Variables para Machine Learning |

---

## 16. Modelo Customer 360

El modelo final permite obtener una vista consolidada de cada cliente a partir de:

- Información básica del cliente.
- Segmento comercial.
- Historial de compras.
- Cantidad de productos comprados.
- Importe total gastado.
- Ticket promedio.
- Fecha de última compra.
- Diversidad de productos adquiridos.

Esta información constituye la base para el análisis de comportamiento y la generación de variables utilizadas por el modelo de clasificación.

---

## 17. Consumo de datos

Los resultados del pipeline pueden ser consumidos mediante una API REST desarrollada con FastAPI.

El endpoint principal de predicción es:

```text
GET /predict/{customer_id}
```

Ejemplo:

```text
GET /predict/C0001
```

La respuesta contiene:

- identificador del cliente;
- predicción de riesgo;
- etiqueta descriptiva;
- probabilidad estimada de riesgo.

La API también expone documentación interactiva mediante:

```text
/docs
```

---

## 18. Machine Learning

El proyecto implementa un modelo de clasificación para identificar clientes potencialmente en riesgo.

### Algoritmo

Regresión logística (`LogisticRegression`).

### Preprocesamiento

Se utiliza:

- `StandardScaler` para variables numéricas.
- `OneHotEncoder` para variables categóricas.

### Variables categóricas

```text
city
segment
```

### Variables numéricas

```text
total_purchases
total_quantity
total_spent
average_ticket
unique_products
```

### Objetivo

```text
at_risk
```

El modelo se entrena utilizando los datos de `retail_mart.customer_features`.

---

## 19. Resultados del modelo

Las métricas registradas para la ejecución actual son:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.55 |
| Precision | 0.5833 |
| Recall | 0.6364 |
| F1 | 0.6087 |

Las métricas se almacenan en:

`ml/reports/metrics.json`

El modelo entrenado se almacena localmente como artefacto del proyecto y también se registra mediante MLflow.

---

## 20. Tracking y reproducibilidad

El entrenamiento del modelo utiliza MLflow para registrar información relacionada con el experimento.

El experimento utilizado es:

`customer_risk_prediction`

El tracking permite registrar información como:

- parámetros;
- métricas;
- características utilizadas;
- cantidad de registros;
- datos de entrenamiento y prueba;
- modelo generado;
- información de la fuente de datos.

El backend local utilizado durante el desarrollo es SQLite mediante:

`mlflow.db`

La base local de MLflow no forma parte del repositorio Git.

---

## 21. Orquestación

El pipeline completo es orquestado mediante Apache Airflow.

El DAG principal es:

`retail_customer_360`

Las principales tareas son:

```text
generate_synthetic_data
        │
        ├── process_customers
        └── process_sales

ingest_products
        │
        └── process_products

process_customers
process_sales
process_products
        │
        ▼
quality_checks
        │
        ▼
init_retail_db
        │
        ▼
load_staging
        │
        ▼
dbt_build
        │
        ▼
build_features
        │
        ▼
train_model_mlflow
```

Airflow permite controlar el orden de ejecución y las dependencias entre las diferentes etapas del pipeline.

---

## 22. Resumen del flujo de datos

El flujo completo del proyecto puede resumirse de la siguiente manera:

```text
                ┌─────────────────────┐
                │ Clientes CSV        │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │        RAW          │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │    Processing       │
                └──────────┬──────────┘
                           │
                           │
┌─────────────────┐        │        ┌─────────────────────┐
│ Ventas CSV      │────────┘        │ API Productos       │
└─────────────────┘                 └──────────┬──────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │      RAW        │
                                      └────────┬────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │   Processing    │
                                      └────────┬────────┘
                                               │
                                               ▼
                           ┌────────────────────────────────┐
                           │       Quality Checks            │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │          PostgreSQL             │
                           │                                │
                           │       retail_staging            │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │             dbt                  │
                           │                                │
                           │ staging → intermediate → marts │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │          Customer 360           │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │       Customer Features         │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │      Machine Learning           │
                           │       Logistic Regression       │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │         MLflow Tracking         │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │          FastAPI                 │
                           └────────────────────────────────┘
```

---

## 23. Tecnologías relacionadas con los datos

| Componente | Tecnología |
|---|---|
| Fuente de archivos | CSV |
| Fuente REST | DummyJSON Products API |
| RAW | Filesystem local |
| Base de datos | PostgreSQL |
| Procesamiento | Python / Pandas |
| Transformaciones | dbt Core |
| Orquestación | Apache Airflow |
| Machine Learning | scikit-learn |
| Tracking ML | MLflow |
| API | FastAPI |
| Contenedores | Docker / Docker Compose |

---

## 24. Consideraciones

Los datos utilizados en este proyecto son sintéticos y se utilizan con fines académicos y de demostración.

La fuente REST utilizada no representa información productiva de una organización real.

En un entorno productivo deberían incorporarse mecanismos adicionales de seguridad, control de acceso, monitoreo, gestión de secretos, alta disponibilidad y políticas de retención de datos.