
import json
import time
import urllib.request

URL = "http://127.0.0.1:8000/eventos"
TOTAL_EVENTOS = 100
REPETICIONES = 3
TAMANO_LOTE = 10


def enviar_datos(datos):
    cuerpo = json.dumps(datos).encode("utf-8")

    solicitud = urllib.request.Request(
        URL,
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(solicitud, timeout=30) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def medir_individual():
    inicio = time.perf_counter()

    for i in range(TOTAL_EVENTOS):
        enviar_datos({
            "origen": "REST individual",
            "valor": i
        })

    return time.perf_counter() - inicio


def medir_lotes():
    inicio = time.perf_counter()

    for inicio_lote in range(0, TOTAL_EVENTOS, TAMANO_LOTE):
        eventos = [
            {
                "origen": "Batch",
                "valor": i
            }
            for i in range(
                inicio_lote,
                min(inicio_lote + TAMANO_LOTE, TOTAL_EVENTOS)
            )
        ]

        enviar_datos({"eventos": eventos})

    return time.perf_counter() - inicio


def ejecutar_prueba(nombre, funcion):
    tiempos = []

    for repeticion in range(REPETICIONES):
        duracion = funcion()
        tiempos.append(duracion)
        print(
            f"  Repeticion {repeticion + 1}: "
            f"{duracion:.4f} segundos"
        )

    promedio = sum(tiempos) / len(tiempos)
    rendimiento = TOTAL_EVENTOS / promedio

    return {
        "arquitectura": nombre,
        "eventos_por_repeticion": TOTAL_EVENTOS,
        "repeticiones": REPETICIONES,
        "tiempo_promedio_segundos": round(promedio, 6),
        "rendimiento_eventos_segundo": round(rendimiento, 2)
    }


if __name__ == "__main__":
    print("BENCHMARK DE API")
    print(f"Eventos por prueba: {TOTAL_EVENTOS}")
    print(f"Repeticiones: {REPETICIONES}")
    print()

    resultados = []

    print("1. REST: una solicitud por evento")
    resultados.append(
        ejecutar_prueba("REST individual", medir_individual)
    )

    print()
    print("2. Batch: una solicitud por cada lote de 10 eventos")
    resultados.append(
        ejecutar_prueba("Batch", medir_lotes)
    )

    print("\nRESULTADOS FINALES")
    for resultado in resultados:
        print(f"\nArquitectura: {resultado['arquitectura']}")
        print(
            "Tiempo promedio: "
            f"{resultado['tiempo_promedio_segundos']} segundos"
        )
        print(
            "Rendimiento: "
            f"{resultado['rendimiento_eventos_segundo']} eventos/segundo"
        )

    with open("resultados_api.json", "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=4, ensure_ascii=False)

    print("\nResultados guardados en resultados_api.json")
