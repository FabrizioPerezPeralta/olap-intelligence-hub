# 📝 Guía de Redacción de Artículos para el Equipo (Medium / Dev.to / Hashnode)

Esta guía define la estructura, los enfoques individuales y los estándares de calidad para que **cada integrante del equipo** redacte y publique un artículo original, profesional y de alto impacto sobre la solución OLAP implementada.

---

## 🎯 Requisitos de la Publicación

1. **Plataformas Aceptadas:** [Dev.to](https://dev.to/), [Medium](https://medium.com/), o [Hashnode](https://hashnode.com/).
2. **Extensión sugerida:** 1,000 - 1,800 palabras (aprox. 5 a 8 minutos de lectura).
3. **Enlaces Oficiales Obligatorios en cada Artículo:**
   * **Repositorio Público en GitHub:** [https://github.com/FabrizioPerezPeralta/olap-intelligence-hub.git](https://github.com/FabrizioPerezPeralta/olap-intelligence-hub.git)
   * **Aplicación en Vivo (Streamlit Cloud):** [https://olap-intelligence-app.streamlit.app](https://olap-intelligence-app.streamlit.app)
4. **Elementos obligatorios en cada artículo:**
   - Explicación conceptual clara de qué es **OLAP** y por qué se diferencia de **OLTP**.
   - Justificación de la tecnología elegida (**DuckDB / MotherDuck**).
   - Diagrama de arquitectura o flujo de datos.
   - Fragmentos de código comentados (SQL OLAP, Python o CI/CD).
   - Capturas de pantalla del dashboard en funcionamiento.
   - Mención explícita de la infraestructura en la nube pública utilizada (sin AWS).

---

## 👥 Asignación de Enfoques por Integrante

Para que los artículos de los miembros del equipo no sean redundantes, cada integrante debe enfocar el desarrollo desde una perspectiva técnica distinta:

---

### 📌 Integrante 1: "Arquitectura y Rendimiento del Motor OLAP: DuckDB & MotherDuck"
* **Objetivo:** Enfocarse en el motor analítico, el almacenamiento columnar y la velocidad de vectorización en la nube.
* **Propuestas de Título:**
  * *"Por qué DuckDB y MotherDuck están redefiniendo el procesamiento analítico (OLAP) en la nube"*
  * *"Construyendo un Data Warehouse Serverless con DuckDB y MotherDuck sin usar AWS"*
  * *"De archivos Parquet a Consultas en Milisegundos: Arquitectura OLAP con DuckDB"*
* **Estructura sugerida del artículo:**
  1. **Introducción:** Límites de las bases de datos transaccionales (OLTP) frente a consultas analíticas masivas.
  2. **¿Qué hace especial a DuckDB?:** Ejecución vectorizada, almacenamiento columnar y cero dependencias pesadas.
  3. **Llevando DuckDB a la Nube con MotherDuck:** Cómo opera este SaaS público, gestión de conexiones y seguridad de tokens.
  4. **El Esquema Analítico:** Análisis de las 150,000 filas en formato Parquet, tipos de datos y compresión ZSTD.
  5. **Benchmarks y Rendimiento:** Demostración de cómo se ejecutan agregaciones y Window Functions en menos de 10-20 ms.
  6. **Conclusión y Enlaces:** Repositorio y aplicación en vivo.

---

### 📌 Integrante 2: "Operaciones OLAP y Visualización Interactiva con Streamlit"
* **Objetivo:** Enfocarse en el análisis multidimensional: Roll-up, Drill-down, Slice & Dice, y cómo se traduce esto en la interfaz analítica.
* **Propuestas de Título:**
  * *"Diseñando un Centro de Inteligencia de Negocios Interactivo con Streamlit y DuckDB"*
  * *"Dominando las 4 Operaciones Clave de OLAP: Roll-Up, Drill-Down, Slice & Dice con Python"*
  * *"De Consultas SQL a Dashboards Ejecutivos: Análisis Dimensional en Tiempo Real"*
* **Estructura sugerida del artículo:**
  1. **Introducción:** La importancia de los dashboards analíticos en la toma de decisiones empresariales.
  2. **Fundamentos OLAP en la práctica:**
     - **Slice & Dice:** Filtros cruzados por geografía, categoría y clientes.
     - **Roll-Up / Drill-Down:** Desglose temporal (de año a mes o día de la semana).
     - **Pivot:** Cruce matricial usando la cláusula `PIVOT` de DuckDB.
  3. **Implementación de la UI en Streamlit:**
     - Uso de `@st.cache_resource` para mantener la conexión optimizada.
     - Gráficos interactivos con Plotly (barras, series temporales de doble eje, heatmaps).
  4. **La Consola SQL Ad-Hoc:** Permitir a usuarios avanzados ejecutar `GROUP BY CUBE` y consultas libres.
  5. **Conclusión y Demo en Vivo:** Enlace a la app pública en Streamlit Cloud.

---

### 📌 Integrante 3: "Automatización de Pipelines Analíticos con CI/CD en GitHub Actions"
* **Objetivo:** Enfocarse en la ingeniería de despliegue, pruebas unitarias para consultas analíticas y despliegue continuo en la nube.
* **Propuestas de Título:**
  * *"CI/CD para Analítica de Datos: Automatizando Pruebas y Despliegues OLAP con GitHub Actions"*
  * *"Ingeniería de Software aplicada a Business Intelligence: Testing analítico y despliegue continuo"*
  * *"Cómo automatizar el ciclo de vida de una solución OLAP en la nube pública paso a paso"*
* **Estructura sugerida del artículo:**
  1. **Introducción:** La necesidad de calidad y automatización en proyectos de datos (DataOps).
  2. **Diseño de la Suite de Pruebas (Pytest):**
     - Cómo verificar que el esquema de datos no esté roto.
     - Pruebas unitarias para validar que los KPIs calculen valores lógicos.
     - Validación de funciones de ventana analíticas (ej. running totals crecientes).
  3. **El Flujo de GitHub Actions:**
     - Explicación paso a paso del archivo `.github/workflows/ci.yml`.
     - Linting y control de calidad con Ruff.
  4. **Despliegue Continuo (CD) en la Nube Pública:**
     - Integración con Streamlit Community Cloud mediante webhooks de Git.
     - Gestión segura de secretos (`MOTHERDUCK_TOKEN`).
  5. **Conclusiones y Aprendizajes:** Buenas prácticas para proyectos de BI reproducibles.

---

## 💡 Consejos de Redacción y Formato

1. **Etiquetas / Tags recomendadas para publicar:**
   `#businessintelligence` `#dataengineering` `#duckdb` `#python` `#devops` `#datascience`
2. **Call to Action (Llamado a la acción):**
   Al final de tu artículo, invita a los lectores a dejar una estrella en el repositorio de GitHub y probar la aplicación web desplegada.
3. **Revisión antes de publicar:**
   - Verifica que los enlaces al repositorio de GitHub y a la app en Streamlit Cloud funcionen.
   - Revisa que las capturas de pantalla se vean nítidas.
   - Pasa el texto por un corrector ortográfico y de estilo.
