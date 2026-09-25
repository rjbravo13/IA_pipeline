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
- control de cambios.

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

---

## 3. Clasificación de los datos

Los datos utilizados en el proyecto se clasifican de acuerdo con su naturaleza y finalidad.

| Tipo de dato | Ejemplos | Clasificación |
|---|---|---|
| Identificadores sintéticos | `customer_id`, `sale_id`, `product_id` | Datos de prueba |
| Datos de clientes sintéticos | ciudad, segmento, fecha de registro | Datos de prueba |
| Datos de ventas sintéticos | cantidad, precio, fecha | Datos de prueba |
| Datos de productos | categoría, marca, descripción, precio | Datos de prueba |
| Features ML | `recency_days`, `at_risk` | Datos derivados |
| Métricas ML | accuracy, precision, recall, F1 | Datos derivados |

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

Una falla en las pruebas de calidad debe ser considerada antes de utilizar los datos para las etapas posteriores del pipeline.

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

Cuando una validación crítica falla, el pipeline debe detener la ejecución de las etapas posteriores o evitar que los datos inválidos sean utilizados.

---

## 7. Trazabilidad

La trazabilidad permite conocer el origen y las transformaciones aplicadas a los datos.

El flujo de trazabilidad es:

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

Los archivos obtenidos desde la API de productos incorporan una marca temporal en el nombre:

```text
products_YYYYMMDD_HHMMSS.json
```

Esto permite identificar diferentes ejecuciones de ingesta.

---

## 8. Identificación de ejecuciones

El pipeline es ejecutado mediante Apache Airflow.

El DAG principal es:

```text
retail_customer_360
```

Cada ejecución del DAG permite identificar una corrida específica del pipeline.

Airflow mantiene el historial de ejecuciones y estados de las tareas.

MLflow mantiene información relacionada con los experimentos de Machine Learning.

---

## 9. Machine Learning y reproducibilidad

El entrenamiento del modelo se realiza mediante scikit-learn y se registra mediante MLflow.

El experimento utilizado es:

```text
customer_risk_prediction
```

La información registrada incluye:

- parámetros;
- métricas;
- variables utilizadas;
- cantidad de registros;
- datos de entrenamiento y prueba;
- modelo generado;
- información de la fuente de datos.

Las métricas principales incluyen:

- accuracy;
- precision;
- recall;
- F1.

Esto permite relacionar un modelo con los datos y configuración utilizados durante su entrenamiento.

---

## 10. Gestión de modelos

Los modelos entrenados se almacenan como artefactos del proyecto.

Durante el desarrollo se utiliza:

```text
ml/models/
```

Los artefactos generados localmente no deben incluirse en el repositorio Git cuando estén cubiertos por `.gitignore`.

MLflow permite mantener información adicional sobre el experimento y el modelo generado.

---

## 11. Seguridad

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

no debe ser incluido en el repositorio Git.

El `.gitignore` contiene la regla:

```text
.env
```

para evitar publicar credenciales o configuraciones locales.

---

## 12. Gestión de secretos

Las credenciales no deben escribirse directamente en los scripts ni almacenarse en el repositorio.

Las configuraciones utilizadas por los contenedores se obtienen mediante variables de entorno.

En un entorno productivo se recomienda utilizar un sistema dedicado de gestión de secretos, por ejemplo:

- AWS Secrets Manager;
- Azure Key Vault;
- Google Secret Manager;
- HashiCorp Vault.

---

## 13. Control de acceso

Durante el desarrollo local, los servicios se ejecutan dentro del entorno Docker del proyecto.

El acceso a PostgreSQL y otros componentes se controla mediante credenciales configuradas mediante variables de entorno.

En un entorno productivo se deberían implementar:

- autenticación;
- autorización;
- roles;
- mínimo privilegio;
- separación de ambientes;
- auditoría de accesos.

---

## 14. Protección de datos

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

## 15. Retención de datos

La capa RAW permite conservar los datos originales durante el desarrollo y facilita la trazabilidad del pipeline.

Los datos generados localmente no forman parte del repositorio Git.

Se consideran artefactos locales:

```text
raw/
mlruns/
mlflow.db
dbt/target/
dbt/logs/
```

Estos elementos se encuentran excluidos mediante `.gitignore`.

En producción, la política de retención deberá definirse de acuerdo con:

- necesidades del negocio;
- requisitos legales;
- costos de almacenamiento;
- necesidades de auditoría;
- requisitos de recuperación.

---

## 16. Control de cambios

El código fuente se administra mediante Git.

El repositorio contiene:

```text
Git
  ↓
main
  ↓
GitHub
```

Los cambios relevantes se registran mediante commits descriptivos.

Ejemplo:

```text
feat: integrate dbt into retail pipeline
```

Los archivos generados y datos locales no deben incluirse en el repositorio cuando no sean necesarios para reproducibilidad del código.

---

## 17. Ambientes

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

---

## 18. Monitoreo

Airflow permite supervisar la ejecución del pipeline mediante el estado de las tareas.

Las ejecuciones pueden terminar en estados como:

```text
SUCCESS
FAILED
RUNNING
QUEUED
```

Los controles de calidad permiten detectar problemas en los datos antes de ejecutar las etapas posteriores.

MLflow permite realizar seguimiento de experimentos y métricas de Machine Learning.

---

## 19. Manejo de errores

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

Esto permite evitar que errores de calidad o procesamiento se propaguen hacia las capas posteriores.

---

## 20. Responsabilidades de las principales herramientas

| Componente | Responsabilidad |
|---|---|
| Filesystem | Conservación de datos RAW |
| Python / Pandas | Procesamiento inicial |
| PostgreSQL | Almacenamiento estructurado |
| dbt | Transformaciones y pruebas SQL |
| Airflow | Orquestación |
| scikit-learn | Entrenamiento del modelo |
| MLflow | Tracking y reproducibilidad |
| FastAPI | Exposición de resultados |
| Git | Control de versiones |
| Docker | Reproducibilidad del entorno |

---

## 21. Datos sintéticos

Los datos de clientes y ventas utilizados en el proyecto son generados artificialmente.

La generación de datos se realiza mediante:

```text
ingestion/generate_synthetic_data.py
```

Estos datos tienen como finalidad permitir el desarrollo y validación del pipeline sin utilizar información real.

---

## 22. Fuente externa de productos

Los productos son obtenidos desde una API REST externa:

```text
DummyJSON Products API
```

Los datos obtenidos se almacenan inicialmente en RAW antes de ser procesados.

Esto permite mantener la trazabilidad entre la fuente externa y los datos utilizados posteriormente por el pipeline.

---

## 23. Principios de gobierno

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
10. Los artefactos locales generados durante la ejecución deben mantenerse fuera del repositorio cuando no sean necesarios.

---

## 24. Consideraciones para producción

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
- control de acceso basado en roles.

Estas medidas dependerían de los requisitos específicos de la organización y del entorno donde se desplegara la solución.