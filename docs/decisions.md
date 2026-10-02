# Decisiones técnicas

Este documento registra las principales decisiones técnicas adoptadas para la implementación del proyecto **Retail Customer 360**, incluyendo las alternativas consideradas, los motivos de selección, los trade-offs y los posibles cambios para un escenario productivo.

---

## 1. Almacenamiento de datos RAW

### Decisión

Utilizar **Filesystem local** como mecanismo de almacenamiento de la zona RAW.

### Alternativas consideradas

- MinIO.
- Object Storage administrado, como Amazon S3 o Azure Blob Storage.

### Motivo

Se eligió Filesystem local porque el proyecto se ejecuta en un entorno local y académico. Permite conservar los archivos originales de las fuentes antes de aplicar transformaciones y mantener trazabilidad mediante archivos con marca temporal de ingesta.

Además, evita incorporar infraestructura adicional para el alcance actual del proyecto.

### Trade-offs

**Se gana:**

- Simplicidad de implementación.
- Facilidad de inspección y depuración de los archivos.
- Bajo costo de infraestructura.
- Facilidad para ejecutar el proyecto localmente.

**Se sacrifica:**

- Escalabilidad del almacenamiento.
- Alta disponibilidad.
- Administración centralizada de los archivos.
- Capacidades propias de un almacenamiento de objetos empresarial.

### Cambio futuro

En un entorno productivo, el Filesystem local podría reemplazarse por un Object Storage como Amazon S3, Azure Blob Storage, Google Cloud Storage o MinIO, dependiendo de la infraestructura disponible.

---

## 2. Base de datos

### Decisión

Utilizar **PostgreSQL** como base de datos para las capas de datos procesados y modelados.

### Alternativas consideradas

- DuckDB.
- Otra base de datos relacional administrada.
- Data Warehouse administrado.

### Motivo

PostgreSQL permite representar las diferentes capas del modelo de datos, establecer relaciones entre entidades y servir los datos procesados a otros componentes del proyecto.

También facilita la integración con **dbt, Airflow y FastAPI**, componentes utilizados en la solución.

### Trade-offs

**Se gana:**

- Modelo relacional ampliamente utilizado.
- Integración sencilla con dbt.
- Soporte para relaciones, restricciones y consultas SQL.
- Facilidad de ejecución local mediante Docker.
- Integración con los demás componentes del pipeline.

**Se sacrifica:**

- Escalabilidad horizontal frente a plataformas de datos distribuidas.
- Capacidades avanzadas de un Data Warehouse administrado.
- Alta disponibilidad y administración empresarial cuando se ejecuta localmente.

### Cambio futuro

En producción podría utilizarse PostgreSQL administrado o migrarse a un Data Warehouse dependiendo del volumen de datos, disponibilidad, rendimiento y necesidades de escalabilidad.

---

## 3. Procesamiento de datos

### Decisión

Utilizar **Python y Pandas** para la limpieza, transformación, estandarización y procesamiento inicial de los datos.

### Alternativas consideradas

- PySpark.
- Otro motor de procesamiento distribuido.
- Transformaciones exclusivamente mediante SQL.

### Motivo

Pandas resulta suficiente para el volumen de datos utilizado en el proyecto y permite implementar de forma sencilla las operaciones de limpieza, tipado, deduplicación, estandarización y validación.

Además, permite mantener el procesamiento reproducible y fácil de ejecutar en el entorno local.

### Trade-offs

**Se gana:**

- Simplicidad de desarrollo.
- Facilidad de mantenimiento.
- Amplio soporte de librerías de análisis de datos.
- Ejecución sencilla en un entorno local.
- Facilidad para realizar transformaciones y validaciones.

**Se sacrifica:**

- Capacidad para manejar grandes volúmenes de datos distribuidos.
- Escalabilidad horizontal.
- Capacidad de procesamiento distribuido propia de motores como Spark.

### Cambio futuro

Para volúmenes significativamente mayores se podría utilizar **PySpark** u otro motor distribuido, manteniendo las mismas etapas lógicas del pipeline.

---

## 4. Transformaciones y modelado

### Decisión

Utilizar **dbt Core** para las transformaciones y el modelado de datos en PostgreSQL.

### Alternativas consideradas

- Transformaciones exclusivamente mediante scripts Python.
- Transformaciones exclusivamente mediante SQL.
- Una plataforma administrada de dbt.

### Motivo

dbt permite organizar las transformaciones mediante modelos separados por capas y facilita la implementación de pruebas de calidad sobre los modelos.

El proyecto utiliza las capas:

- staging
- intermediate
- marts

También se utilizan pruebas como:

- `not_null`
- `unique`
- `relationships`

Esto facilita la trazabilidad y mantenimiento de las transformaciones.

### Trade-offs

**Se gana:**

- Organización por capas.
- Transformaciones SQL estructuradas.
- Pruebas de calidad integradas.
- Trazabilidad de los modelos.
- Facilidad de mantenimiento.
- Integración con PostgreSQL.

**Se sacrifica:**

- Requiere incorporar dbt como componente adicional.
- Agrega una etapa adicional al pipeline.
- La solución local no dispone de las capacidades operativas de una plataforma administrada.

### Cambio futuro

En producción se podría utilizar **dbt en un entorno administrado** o integrarlo con una plataforma de datos empresarial y CI/CD.

---

## 5. Orquestación

### Decisión

Utilizar **Apache Airflow 3 ejecutado mediante Docker** para la orquestación del pipeline.

### Alternativas consideradas

- Cron.
- Scripts independientes ejecutados manualmente.
- Una plataforma administrada de orquestación.

### Motivo

Airflow permite representar las dependencias entre las diferentes etapas del pipeline y centralizar su ejecución mediante un DAG reproducible.

El DAG `retail_customer_360` integra las principales etapas del proyecto:

1. Generación de datos sintéticos.
2. Ingesta de productos.
3. Procesamiento.
4. Controles de calidad.
5. Carga de staging.
6. Ejecución de dbt.
7. Construcción de features.
8. Entrenamiento del modelo.

Además, se configuraron reintentos para las tareas mediante `retries` y `retry_delay`.

### Trade-offs

**Se gana:**

- Orquestación centralizada.
- Definición explícita de dependencias.
- Ejecución reproducible.
- Reintentos ante errores.
- Visibilidad del estado de las tareas.
- Facilidad para ampliar el pipeline.

**Se sacrifica:**

- Mayor complejidad frente a utilizar cron.
- Consumo adicional de recursos.
- Necesidad de administrar componentes de Airflow en el entorno local.

### Cambio futuro

En producción se podría utilizar **Airflow administrado** u otra plataforma de orquestación empresarial, manteniendo la estructura lógica de dependencias del pipeline.

---

## 6. Machine Learning

### Decisión

Utilizar **scikit-learn** para implementar el modelo de clasificación de riesgo de clientes.

### Alternativas consideradas

- PySpark ML.
- Otras librerías de machine learning.
- Plataformas administradas de Machine Learning.

### Motivo

El volumen de datos utilizado en el proyecto permite utilizar scikit-learn para implementar un modelo de clasificación sencillo y reproducible.

Se utiliza un pipeline de Machine Learning compuesto por:

- `OneHotEncoder`
- `StandardScaler`
- `LogisticRegression`

El modelo se evalúa utilizando métricas de clasificación como:

- accuracy
- precision
- recall
- f1

### Trade-offs

**Se gana:**

- Implementación sencilla.
- Facilidad de entrenamiento y evaluación.
- Amplio soporte de librerías.
- Reproducibilidad.
- Integración sencilla con Python y MLflow.

**Se sacrifica:**

- Escalabilidad para datasets de gran tamaño.
- Capacidad de procesamiento distribuido.
- Menor flexibilidad frente a soluciones de Machine Learning especializadas para grandes volúmenes.

### Cambio futuro

Para mayores volúmenes de datos se podría evaluar **PySpark ML** u otra plataforma de Machine Learning distribuido.

---

## 7. Tracking de experimentos

### Decisión

Utilizar **MLflow** para registrar los experimentos y la trazabilidad del entrenamiento del modelo.

### Alternativas consideradas

- Registro manual de métricas.
- Archivos JSON o CSV.
- Una plataforma administrada de Machine Learning.

### Motivo

MLflow permite registrar parámetros, métricas, información del modelo y datos relacionados con cada ejecución del entrenamiento.

El proyecto registra información como:

- `run_id`
- `training_timestamp`
- `dataset_version`
- `feature_columns`
- algoritmo y parámetros del modelo
- métricas de evaluación
- versión del modelo

Esto permite relacionar el entrenamiento con el modelo generado y mejorar la reproducibilidad.

### Trade-offs

**Se gana:**

- Trazabilidad de experimentos.
- Registro centralizado de métricas.
- Identificación de ejecuciones mediante `run_id`.
- Registro de parámetros y características utilizadas.
- Mayor reproducibilidad del entrenamiento.

**Se sacrifica:**

- Incorporación de un componente adicional.
- Necesidad de administrar el tracking server y almacenamiento local.
- Menor disponibilidad y escalabilidad frente a una plataforma administrada.

### Cambio futuro

En producción se podría utilizar un backend de MLflow administrado o una plataforma de Machine Learning con capacidades de experiment tracking, model registry y almacenamiento de artefactos.

---

## 8. API de consumo

### Decisión

Utilizar **FastAPI** para exponer las predicciones del modelo mediante una API REST.

### Alternativas consideradas

- Consumo directo desde PostgreSQL.
- Aplicación web integrada.
- Plataforma administrada para despliegue de APIs.

### Motivo

FastAPI permite exponer los resultados del modelo mediante endpoints REST y proporciona documentación interactiva mediante OpenAPI.

El endpoint de predicción permite consultar el riesgo de un cliente mediante su `customer_id`.

La respuesta incluye información de trazabilidad de la predicción, como:

- `prediction_timestamp`
- `model_version`
- `run_id`
- probabilidad de riesgo
- resultado de la predicción

### Trade-offs

**Se gana:**

- API REST sencilla de implementar.
- Documentación automática mediante OpenAPI.
- Integración sencilla con Python.
- Separación entre el modelo y el consumidor.
- Facilidad para realizar pruebas mediante Swagger.

**Se sacrifica:**

- Requiere administrar un servicio adicional.
- La implementación local no incluye características empresariales completas de seguridad y observabilidad.
- Requiere definir mecanismos adicionales de autenticación y autorización para producción.

### Cambio futuro

La API podría desplegarse en una plataforma administrada, detrás de un API Gateway, incorporando autenticación, autorización, observabilidad, control de acceso y escalabilidad horizontal.

---

## 9. Contenedores

### Decisión

Utilizar **Docker Compose** para ejecutar los principales componentes de infraestructura del proyecto.

### Alternativas consideradas

- Ejecución directa de todos los componentes en el sistema operativo.
- Kubernetes.
- Plataformas de contenedores administradas.

### Motivo

Docker Compose permite ejecutar PostgreSQL, Airflow y los demás componentes de infraestructura de forma reproducible en el entorno local.

También facilita la configuración de dependencias, redes y servicios necesarios para ejecutar el proyecto.

### Trade-offs

**Se gana:**

- Reproducibilidad del entorno.
- Configuración centralizada.
- Facilidad para levantar y detener los servicios.
- Aislamiento de dependencias.
- Facilidad para compartir el proyecto.

**Se sacrifica:**

- Menor escalabilidad frente a Kubernetes.
- No proporciona por sí mismo alta disponibilidad.
- Requiere recursos locales para ejecutar múltiples servicios.

### Cambio futuro

En producción los servicios podrían desplegarse mediante **Kubernetes** u otra plataforma de contenedores administrada.

---

## 10. Fuente REST

### Decisión

Utilizar **DummyJSON Products API** como segunda fuente de datos externa.

### Alternativas consideradas

- Una API comercial de productos.
- Una API empresarial.
- Un segundo archivo local como fuente adicional.

### Motivo

DummyJSON permite disponer de una fuente REST externa para cumplir el requisito de integración con una segunda fuente de datos sin requerir credenciales.

La respuesta obtenida desde la API se conserva inicialmente en la zona RAW antes de ser procesada.

### Trade-offs

**Se gana:**

- Integración con una fuente REST real.
- No requiere credenciales.
- Facilidad de ejecución y reproducción del proyecto.
- Permite demostrar la integración de múltiples fuentes.

**Se sacrifica:**

- No representa las características operativas de una API empresarial real.
- Dependencia de la disponibilidad de un servicio externo.
- Menor control sobre cambios en la fuente externa.

### Cambio futuro

En producción la fuente podría reemplazarse por una API empresarial con autenticación, contratos de servicio, monitoreo, controles de disponibilidad y gestión de cambios.

---

## Resumen de decisiones

| Componente | Decisión actual | Posible evolución |
|---|---|---|
| RAW | Filesystem local | Object Storage |
| Base de datos | PostgreSQL | PostgreSQL administrado / Data Warehouse |
| Procesamiento | Python + Pandas | PySpark / procesamiento distribuido |
| Transformaciones | dbt Core | dbt administrado / plataforma de datos |
| Orquestación | Airflow + Docker | Airflow administrado |
| Machine Learning | scikit-learn | ML distribuido / plataforma ML |
| Tracking | MLflow local | MLflow administrado / ML platform |
| API | FastAPI | API administrada / API Gateway |
| Contenedores | Docker Compose | Kubernetes / plataforma administrada |
| Fuente REST | DummyJSON | API empresarial |