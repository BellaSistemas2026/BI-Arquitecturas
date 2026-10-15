import time
import json
import statistics
import urllib.request

API_URL = "http://127.0.0.1:8000/eventos"
TOTAL_EVENTOS = 100

def enviar_evento_individual(i):
    datos = json.dumps({
        "origen": "REST individual",
        "valor": i
    }).encode("utf-8")

    solicitud = urllib.request.Request(
        API_URL,
        data=datos,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(solicitud) as respuesta:
        respuesta.read()

def probar_api_individual():
    inicio = time.perf_counter()

    for i in range(TOTAL_EVENTOS):
        enviar_evento_individual(i)

    return time.perf_counter() - inicio

def probar_api_lotes():
    inicio = time.perf_counter()

    # Simulación local del procesamiento por lotes.
    # Se agrupan los eventos antes de procesarlos.
    eventos = [
        {"origen": "Batch", "valor": i}
        for i in range(TOTAL_EVENTOS)
    ]

    for inicio_lote in range(0, TOTAL_EVENTOS, 10):
        lote = eventos[inicio_lote:inicio_lote + 10]

        for evento in lote:
            enviar_evento_individual(evento["valor"])

    return time.perf_counter() - inicio

def medir(funcion, repeticiones=3):
    tiempos = []

    for _ in range(repeticiones):
        tiempos.append(funcion())

    return statistics.mean(tiempos)

if __name__ == "__main__":
    print("BENCHMARK DE ARQUITECTURAS DE API")
    print("-" * 45)

    tiempo_rest = medir(probar_api_individual)
    tiempo_batch = medir(probar_api_lotes)

    resultados = [
        {
            "arquitectura": "REST individual",
            "eventos": TOTAL_EVENTOS,
            "tiempo_promedio_segundos": round(tiempo_rest, 6),
            "eventos_por_segundo": round(TOTAL_EVENTOS / tiempo_rest, 2)
        },
        {
            "arquitectura": "Procesamiento por lotes (Batch)",
            "eventos": TOTAL_EVENTOS,
            "tiempo_promedio_segundos": round(tiempo_batch, 6),
            "eventos_por_segundo": round(TOTAL_EVENTOS / tiempo_batch, 2)
        }
    ]

    for resultado in resultados:
        print()
        print("Arquitectura:", resultado["arquitectura"])
        print("Eventos:", resultado["eventos"])
        print("Tiempo promedio:",
              resultado["tiempo_promedio_segundos"], "segundos")
        print("Rendimiento:",
              resultado["eventos_por_segundo"], "eventos/segundo")

    with open("resultados_api.json", "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=4, ensure_ascii=False)

    print()
    print("Resultados guardados en resultados_api.json")