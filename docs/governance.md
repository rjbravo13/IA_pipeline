# Gobierno y gestión de datos

## 1. Objetivo

Este documento define los principios utilizados para gestionar los datos dentro del proyecto Retail Customer 360.

El objetivo es establecer criterios para:

- calidad de datos;
- trazabilidad;
- seguridad;
- acceso;
- manejo de información sensible;
- retención;
- reproducibilidad;
- control de cambios;
- gestión de modelos de Machine Learning.

El proyecto utiliza datos sintéticos con fines académicos y de demostración.

---

## 2. Alcance

Las políticas descritas aplican a las principales etapas del pipeline:

```text
Fuente
  ↓
RAW
  ↓
Processing
  ↓
Quality
  ↓
Staging
  ↓
dbt
  ↓
Customer 360
  ↓
Features
  ↓
Machine Learning
  ↓
API
```

El gobierno de datos considera tanto los datos originales como los datos transformados, derivados y utilizados por Machine Learning.

---

## 3. Clasificación de los datos

Los datos utilizados en el proyecto se clasifican de acuerdo con su naturaleza y finalidad.

| Tipo de dato | Ejemplos | Clasificación |
|---|---|---|
| Identificadores sintéticos | `customer_id`, `sale_id`, `product_id` | Datos de prueba |
| Datos de clientes sintéticos | ciudad, segmento, fecha de registro | Datos de prueba |
| Datos de ventas sintéticos | cantidad, precio, fecha | Datos de prueba |
| Datos de productos | categoría, marca, descripción, precio | Datos de prueba |
| Features ML | `recency_days`, `total_spent`, `average_ticket` | Datos derivados |
| Variable objetivo | `at_risk` | Dato derivado |
| Métricas ML | accuracy, precision, recall, F1 | Datos derivados |
| Metadata del modelo | `run_id`, `model_version`, `training_timestamp` | Metadata técnica |
| Predicciones | `at_risk`, `risk_probability` | Datos derivados |

No se utilizan datos personales reales en el proyecto.

---

## 4. Calidad de datos

La calidad de los datos se controla antes de que la información avance hacia las capas posteriores.

Las principales reglas implementadas incluyen:

- identificadores obligatorios;
- unicidad de identificadores;
- cantidades mayores que cero;
- precios mayores o iguales a cero;
- fechas válidas;
- relaciones entre entidades;
- consistencia de los importes calculados.

Las validaciones generales se ejecutan mediante:

```text
quality/quality_checks.py
```

Los resultados se almacenan en:

```text
quality/reports/quality_report.json
```

Las validaciones permiten detectar errores antes de que los datos sean utilizados por PostgreSQL, dbt y Machine Learning.

---

## 5. Reglas de calidad en dbt

Los modelos dbt cuentan con pruebas automatizadas para validar la integridad de los datos.

Se utilizan principalmente:

```text
not_null
unique
relationships
```

Estas pruebas se aplican sobre los modelos de staging y mart.

Las pruebas permiten validar que los identificadores obligatorios existan, que los campos que deben ser únicos no presenten duplicados y que las relaciones entre entidades sean consistentes.

---

## 6. Reglas bloqueantes

El proyecto contempla reglas de calidad que pueden impedir la continuación del procesamiento cuando los datos no cumplen condiciones mínimas.

Entre las condiciones consideradas se encuentran:

- identificadores de cliente nulos;
- identificadores de producto nulos;
- cantidades inválidas;
- precios inválidos;
- identificadores de venta duplicados;
- relaciones inexistentes entre entidades.

Cuando una validación crítica falla, el proceso de calidad genera una excepción:

```text
RuntimeError("Proceso detenido por fallos de calidad.")
```

Esto evita que datos que no cumplen las condiciones mínimas continúen hacia las siguientes etapas del pipeline.

---

## 7. Trazabilidad de datos

La trazabilidad permite conocer el origen y las transformaciones aplicadas a los datos.

El flujo general de trazabilidad es:

```text
Fuente
  ↓
RAW
  ↓
Processing
  ↓
Quality
  ↓
Staging
  ↓
dbt
  ↓
Customer 360
  ↓
Features
  ↓
Machine Learning
  ↓
API
```

Los datos originales se conservan en la capa RAW antes de aplicar transformaciones.

Los archivos de clientes y ventas utilizan una marca temporal:

```text
customers_YYYYMMDD_HHMMSS.csv
sales_YYYYMMDD_HHMMSS.csv
```

Los productos obtenidos desde la API REST utilizan una marca temporal:

```text
products_YYYYMMDD_HHMMSS.json
```

Esto permite diferenciar las diferentes ejecuciones de ingesta.

---

## 8. Identificación de ejecuciones

El pipeline es ejecutado y orquestado mediante Apache Airflow.

El DAG principal es:

```text
retail_customer_360
```

Airflow mantiene información sobre las ejecuciones del DAG y el estado de las tareas.

La ejecución del pipeline se divide en tareas con dependencias definidas.

Las tareas utilizan mecanismos de reintento para errores transitorios:

```text
retries: 2
retry_delay: 2 minutos
```

---

## 9. Machine Learning y reproducibilidad

El entrenamiento del modelo se realiza mediante scikit-learn y se registra mediante MLflow.

El experimento utilizado es:

```text
customer_risk_prediction
```

La ejecución de entrenamiento registra información relacionada con:

- algoritmo;
- hiperparámetros;
- métricas;
- variables utilizadas;
- cantidad de registros;
- dataset utilizado;
- fecha y hora de entrenamiento;
- versión del modelo;
- identificador de ejecución.

Los principales elementos de trazabilidad registrados por MLflow son:

```text
run_id
model_version
training_timestamp
dataset_version
feature_columns
```

Las métricas principales incluyen:

```text
accuracy
precision
recall
f1
```

Esto permite relacionar una ejecución de entrenamiento con el dataset, las variables, la configuración y el modelo generado.

---

## 10. Metadata del modelo

El modelo entrenado se almacena localmente como:

```text
ml/models/customer_risk_model_mlflow.joblib
```

Adicionalmente, se genera un archivo de metadata:

```text
ml/models/customer_risk_model_mlflow_metadata.json
```

Este archivo contiene:

```text
run_id
model_version
training_timestamp
dataset_version
feature_columns
target
```

El archivo permite identificar qué ejecución generó el modelo y qué información fue utilizada durante el entrenamiento.

---

## 11. Gestión de modelos

Durante el desarrollo local, los modelos generados se almacenan en:

```text
ml/models/
```

Los artefactos generados localmente están excluidos del repositorio Git mediante `.gitignore`.

Por lo tanto, el modelo debe generarse mediante el proceso de entrenamiento antes de utilizar la API en un entorno limpio.

El entrenamiento se realiza mediante:

```powershell
python ml/train_model_mlflow.py
```

Una vez generado el modelo y su metadata, FastAPI puede cargar los artefactos necesarios para realizar predicciones.

---

## 12. Seguridad

El proyecto utiliza variables de entorno para las credenciales y configuración sensible de infraestructura.

Las variables relacionadas con PostgreSQL se gestionan mediante:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

El archivo:

```text
.env
```

no debe incluirse en el repositorio Git.

El `.gitignore` contiene la regla:

```text
.env
```

para evitar publicar credenciales o configuraciones locales.

---

## 13. Gestión de secretos

Las credenciales no deben escribirse directamente en los scripts ni almacenarse en el repositorio.

Las configuraciones utilizadas por los contenedores se obtienen mediante variables de entorno.

El proyecto utiliza un archivo `.env` únicamente para la configuración local.

El archivo `.env` debe permanecer fuera del control de versiones.

En un entorno productivo se recomienda utilizar un sistema dedicado de gestión de secretos, por ejemplo:

- AWS Secrets Manager;
- Azure Key Vault;
- Google Secret Manager;
- HashiCorp Vault.

---

## 14. Control de acceso

Durante el desarrollo local, los servicios se ejecutan dentro del entorno Docker del proyecto.

El acceso a PostgreSQL y otros componentes se controla mediante credenciales configuradas mediante variables de entorno.

En un entorno productivo se deberían implementar:

- autenticación;
- autorización;
- roles;
- principio de mínimo privilegio;
- separación de ambientes;
- auditoría de accesos.

---

## 15. Protección de datos

El proyecto utiliza datos sintéticos.

Por esta razón, no se procesan datos personales reales.

Si el proyecto fuera adaptado a información real, deberían implementarse medidas adicionales para proteger los datos personales, incluyendo:

- control de acceso;
- cifrado;
- anonimización o pseudonimización cuando corresponda;
- auditoría;
- políticas de retención;
- gestión de consentimiento cuando sea aplicable.

---

## 16. Retención de datos

La capa RAW permite conservar los datos originales durante el desarrollo y facilita la trazabilidad del pipeline.

Los datos generados localmente no forman parte del repositorio Git.

Los principales artefactos locales excluidos del control de versiones son:

```text
raw/
mlruns/
mlflow.db
ml/models/
ml/reports/
dbt/target/
dbt/logs/
airflow/logs/
```

Estos elementos se encuentran contemplados en `.gitignore`.

En producción, la política de retención deberá definirse de acuerdo con:

- necesidades del negocio;
- requisitos legales;
- costos de almacenamiento;
- necesidades de auditoría;
- requisitos de recuperación.

---

## 17. Control de cambios

El código fuente se administra mediante Git.

El repositorio utiliza:

```text
Git
  ↓
main
  ↓
GitHub
```

Los cambios relevantes deben registrarse mediante commits descriptivos.

Ejemplo:

```text
feat: integrate dbt into retail pipeline
```

Los datos generados, logs, modelos locales y otros artefactos temporales no deben incluirse en el repositorio cuando no sean necesarios para reproducir el código.

---

## 18. Ambientes

Durante el desarrollo se utiliza un entorno local basado en Docker Compose.

Los principales componentes son:

```text
PostgreSQL
Airflow
MLflow
FastAPI
dbt
```

El entorno local permite reproducir el pipeline sin depender de infraestructura cloud.

En un escenario productivo se recomienda separar como mínimo:

```text
Desarrollo
   ↓
QA / Pruebas
   ↓
Producción
```

Cada ambiente debería disponer de su propia configuración y credenciales.

---

## 19. Monitoreo

Airflow permite supervisar la ejecución del pipeline mediante el estado de las tareas.

Las ejecuciones pueden presentar estados como:

```text
SUCCESS
FAILED
RUNNING
QUEUED
```

Los controles de calidad permiten detectar problemas en los datos antes de ejecutar las etapas posteriores.

MLflow permite realizar seguimiento de los experimentos y métricas de Machine Learning.

FastAPI permite validar el estado del servicio mediante:

```text
GET /health
```

---

## 20. Manejo de errores

El pipeline está organizado mediante dependencias entre tareas de Airflow.

El flujo general es:

```text
Ingesta
   ↓
Procesamiento
   ↓
Quality Checks
   ↓
Carga
   ↓
dbt
   ↓
Features
   ↓
Machine Learning
```

Si una tarea requerida falla, las tareas dependientes no deberían continuar con datos inválidos.

Las reglas bloqueantes de calidad detienen el procesamiento cuando se detectan errores críticos.

Airflow también utiliza reintentos para errores transitorios:

```text
retries: 2
retry_delay: 2 minutos
```

Esto permite diferenciar errores de calidad de datos de errores transitorios de ejecución.

---

## 21. Responsabilidades de las principales herramientas

| Componente | Responsabilidad |
|---|---|
| Filesystem | Conservación de datos RAW |
| Python / Pandas | Procesamiento inicial |
| PostgreSQL | Almacenamiento estructurado |
| dbt | Transformaciones y pruebas SQL |
| Airflow | Orquestación |
| scikit-learn | Entrenamiento del modelo |
| MLflow | Tracking y trazabilidad de Machine Learning |
| FastAPI | Exposición de predicciones |
| Git | Control de versiones |
| Docker | Reproducibilidad del entorno |

---

## 22. Datos sintéticos

Los datos de clientes y ventas utilizados en el proyecto son generados artificialmente.

La generación de datos se realiza mediante:

```text
ingestion/generate_synthetic_data.py
```

Los archivos generados utilizan una marca temporal para diferenciar las diferentes ejecuciones:

```text
customers_YYYYMMDD_HHMMSS.csv
sales_YYYYMMDD_HHMMSS.csv
```

Estos datos tienen como finalidad permitir el desarrollo y validación del pipeline sin utilizar información real.

---

## 23. Fuente externa de productos

Los productos son obtenidos desde una API REST externa:

```text
DummyJSON Products API
```

Los datos obtenidos se almacenan inicialmente en RAW antes de ser procesados.

Esto permite mantener la trazabilidad entre la fuente externa y los datos utilizados posteriormente por el pipeline.

---

## 24. Trazabilidad de predicciones

La API incorpora información de trazabilidad en cada predicción.

El endpoint principal es:

```text
GET /predict/{customer_id}
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

Los campos:

```text
prediction_timestamp
model_version
run_id
```

permiten identificar cuándo se generó la predicción y qué versión del modelo fue utilizada.

El `run_id` permite relacionar la predicción con la ejecución correspondiente registrada en MLflow.

---

## 25. Principios de gobierno

El proyecto sigue los siguientes principios:

1. Los datos deben conservar trazabilidad desde su origen.
2. Los datos deben validarse antes de ser utilizados en etapas posteriores.
3. Las reglas de calidad deben estar documentadas.
4. Los datos sintéticos deben mantenerse separados de datos productivos.
5. Las credenciales no deben almacenarse en el repositorio.
6. Los cambios de código deben gestionarse mediante control de versiones.
7. Los modelos de Machine Learning deben contar con información de trazabilidad.
8. Las transformaciones deben ser reproducibles.
9. Los datos derivados deben poder relacionarse con sus fuentes.
10. Las predicciones deben poder relacionarse con el modelo utilizado.
11. Los artefactos locales generados durante la ejecución deben mantenerse fuera del repositorio cuando no sean necesarios.
12. Las reglas críticas de calidad deben poder bloquear el procesamiento de datos inválidos.

---

## 26. Consideraciones para producción

La implementación actual está orientada a un entorno local y académico.

Para una implementación productiva deberían considerarse adicionalmente:

- almacenamiento de objetos administrado;
- bases de datos administradas;
- gestión centralizada de secretos;
- autenticación y autorización;
- cifrado de datos;
- monitoreo y alertas;
- auditoría;
- alta disponibilidad;
- backups;
- políticas formales de retención;
- separación de ambientes;
- CI/CD;
- gestión formal del ciclo de vida de modelos;
- control de acceso basado en roles;
- registro y monitoreo de predicciones.

Estas medidas dependerían de los requisitos específicos de la organización y del entorno donde se desplegara la solución.