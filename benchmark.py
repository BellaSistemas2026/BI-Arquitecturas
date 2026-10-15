
import sqlite3
import time
import json
import statistics
from pathlib import Path

DB_NAME = "bi_database.db"
TOTAL_EVENTOS = 10000


def preparar_datos():
    """Genera eventos de prueba reproducibles."""
    return [
        {
            "id": i,
            "origen": f"sensor_{i % 10}",
            "valor": float((i * 17) % 1000),
            "fecha": time.time() + i / 1000
        }
        for i in range(1, TOTAL_EVENTOS + 1)
    ]


def lambda_batch(eventos):
    """Simula ingesta por lotes: carga histórica y actualización reciente."""
    inicio = time.perf_counter()

    # Capa batch: procesa todos los registros en una carga.
    batch = [e for e in eventos if e["valor"] >= 0]

    # Capa speed: procesa los eventos recientes.
    limite = max(0, len(eventos) - 100)
    recientes = [e for e in eventos[limite:] if e["valor"] >= 0]

    # Capa serving: combina los resultados de ambas capas.
    resultado = {
        "arquitectura": "Lambda",
        "eventos_batch": len(batch),
        "eventos_recientes": len(recientes),
        "eventos_totales": len(eventos)
    }

    return resultado, time.perf_counter() - inicio


def kappa_stream(eventos):
    """Simula ingesta mediante un flujo único de eventos."""
    inicio = time.perf_counter()

    total = 0
    suma = 0.0
    por_origen = {}

    for evento in eventos:
        if evento["valor"] >= 0:
            total += 1
            suma += evento["valor"]
            origen = evento["origen"]
            por_origen[origen] = por_origen.get(origen, 0) + 1

    resultado = {
        "arquitectura": "Kappa",
        "eventos_totales": total,
        "suma_valores": suma,
        "origenes": len(por_origen)
    }

    return resultado, time.perf_counter() - inicio


def guardar_resultados(resultados):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS benchmark (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arquitectura TEXT,
                eventos INTEGER,
                tiempo_segundos REAL,
                eventos_por_segundo REAL,
                fecha TEXT
            )
        """)

        for r in resultados:
            conn.execute("""
                INSERT INTO benchmark
                (arquitectura, eventos, tiempo_segundos,
                 eventos_por_segundo, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (
                r["arquitectura"],
                r["eventos"],
                r["tiempo_segundos"],
                r["eventos_por_segundo"],
                r["fecha"]
            ))


def main():
    if not Path(DB_NAME).exists():
        print("No se encuentra la base de datos. Ejecuta primero app.py.")
        return

    eventos = preparar_datos()
    resultados = []

    # Se realizan cinco mediciones por arquitectura.
    for nombre, funcion in [
        ("Lambda", lambda_batch),
        ("Kappa", kappa_stream)
    ]:
        tiempos = []

        for _ in range(5):
            _, duracion = funcion(eventos)
            tiempos.append(duracion)

        promedio = statistics.mean(tiempos)
        rendimiento = len(eventos) / promedio if promedio > 0 else 0

        resultados.append({
            "arquitectura": nombre,
            "eventos": len(eventos),
            "tiempo_segundos": promedio,
            "eventos_por_segundo": rendimiento,
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    guardar_resultados(resultados)

    salida = {
        "tipo": "benchmark local simulado",
        "eventos_generados": len(eventos),
        "mediciones_por_arquitectura": 5,
        "resultados": resultados,
        "nota": (
            "Compara el tiempo de las funciones de procesamiento en memoria; "
            "no mide una plataforma distribuida ni la latencia de red."
        )
    }

    Path("resultados_benchmark.json").write_text(
        json.dumps(salida, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nRESULTADOS DEL BENCHMARK")
    print("-" * 55)

    for r in resultados:
        print(f"Arquitectura: {r['arquitectura']}")
        print(f"Eventos: {r['eventos']}")
        print(f"Tiempo promedio: {r['tiempo_segundos']:.6f} segundos")
        print(f"Rendimiento: {r['eventos_por_segundo']:.2f} eventos/segundo")
        print("-" * 55)

    print("Resultados guardados en resultados_benchmark.json")
    print("Mediciones guardadas en la tabla benchmark de SQLite.")


if __name__ == "__main__":
    main()
