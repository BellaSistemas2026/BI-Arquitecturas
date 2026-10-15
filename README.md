# Comparación de arquitecturas de ingesta de datos y APIs para Business Intelligence

## 1. Descripción del proyecto

Este proyecto implementa un prototipo local para explorar arquitecturas de ingesta de datos y servicios API aplicados a Business Intelligence (BI). Se utiliza Python como lenguaje de programación y SQLite como sistema de almacenamiento.

El propósito es comparar el comportamiento de dos enfoques de procesamiento de datos, Lambda y Kappa, y realizar pruebas iniciales de rendimiento con solicitudes API.

## 2. Objetivos

- Implementar una API local conectada a una base de datos.
- Simular el procesamiento de eventos con las arquitecturas Lambda y Kappa.
- Medir el tiempo de ejecución y el rendimiento de las pruebas.
- Registrar los resultados para su análisis y comparación.

## 3. Tecnologías utilizadas

- Python
- SQLite
- HTTP y JSON
- Git y GitHub

## 4. Arquitecturas de ingesta de datos

### Arquitectura Lambda

Combina el procesamiento por lotes (batch) con una capa de procesamiento rápido (speed layer). En este prototipo se simulan ambos enfoques mediante funciones locales de Python.

### Arquitectura Kappa

Utiliza un enfoque de procesamiento mediante un flujo de eventos. En este prototipo se simula el procesamiento secuencial de eventos en memoria.

## 5. Pruebas de API

Se implementó una API HTTP local con operaciones para consultar e insertar eventos en una base de datos SQLite.

Se realizaron pruebas preliminares con 100 eventos, comparando el envío individual de solicitudes con un enfoque que organiza los eventos en grupos de diez.

Los resultados iniciales fueron:

- REST individual: 2.88075 segundos de tiempo promedio y 34.71 eventos por segundo.
- Enfoque organizado por lotes: 1.356111 segundos de tiempo promedio y 73.74 eventos por segundo.

**Limitación:** el código de la prueba por lotes todavía envía cada evento mediante una solicitud individual. Por ello, los resultados no representan una comparación definitiva entre una API REST individual y una API con un endpoint batch real. La prueba debe mejorarse antes de obtener conclusiones definitivas.

## 6. Resultados de ingesta

El archivo `benchmark.py` ejecuta una simulación local de las arquitecturas Lambda y Kappa con 10 000 eventos. Los resultados se guardan en `resultados_benchmark.json` y en la base de datos SQLite.

Las mediciones dependen del equipo, del código y de las condiciones de ejecución. No representan el rendimiento de plataformas distribuidas en producción.

## 7. Archivos del proyecto

- `app.py`: servidor HTTP y conexión con SQLite.
- `benchmark.py`: simulación y medición de Lambda y Kappa.
- `api_benchmark.py`: pruebas preliminares de rendimiento de API.
- `bi_database.db`: base de datos SQLite.
- `resultados_benchmark.json`: resultados de ingesta.
- `resultados_api.json`: resultados de API.

## 8. Ejecución

Se requiere Python instalado.

1. Iniciar la API con `python app.py`.
2. Abrir otra terminal en la carpeta del proyecto.
3. Ejecutar `python benchmark.py` para medir la simulación Lambda/Kappa.
4. Ejecutar `python api_benchmark.py` para repetir la prueba preliminar de API.

La API local está disponible en `http://127.0.0.1:8000`.

## 9. Conclusión preliminar

El prototipo permite experimentar con diferentes estrategias de procesamiento y registrar sus tiempos de ejecución. Para obtener conclusiones válidas se requiere repetir las mediciones bajo condiciones controladas, implementar un endpoint batch real y documentar las características del entorno de prueba.

Este proyecto tiene fines académicos y constituye una implementación experimental local, no una plataforma distribuida de producción.