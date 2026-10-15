
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

DB_NAME = "bi_database.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origen TEXT NOT NULL,
                valor REAL NOT NULL,
                fecha REAL NOT NULL
            )
        """)


class APIHandler(BaseHTTPRequestHandler):

    def enviar_json(self, codigo, datos):
        cuerpo = json.dumps(datos).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/":
            self.enviar_json(200, {
                "proyecto": "BI Arquitecturas",
                "estado": "funcionando",
                "base_datos": DB_NAME
            })

        elif self.path == "/eventos":
            with sqlite3.connect(DB_NAME) as conn:
                filas = conn.execute(
                    "SELECT id, origen, valor, fecha "
                    "FROM eventos ORDER BY id DESC"
                ).fetchall()

            respuesta = [
                {
                    "id": f[0],
                    "origen": f[1],
                    "valor": f[2],
                    "fecha": f[3]
                }
                for f in filas
            ]
            self.enviar_json(200, respuesta)

        else:
            self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        if self.path != "/eventos":
            self.send_error(404, "Ruta no encontrada")
            return

        try:
            longitud = int(self.headers.get("Content-Length", 0))
            datos = json.loads(
                self.rfile.read(longitud).decode("utf-8")
            )

            fecha = time.time()

            # Una solicitud puede contener varios eventos.
            if isinstance(datos, dict) and "eventos" in datos:
                eventos = datos["eventos"]

                if not isinstance(eventos, list) or not eventos:
                    self.send_error(400, "La lista de eventos no es válida")
                    return

                registros = [
                    (str(evento["origen"]), float(evento["valor"]), fecha)
                    for evento in eventos
                ]

                with sqlite3.connect(DB_NAME) as conn:
                    conn.executemany(
                        "INSERT INTO eventos (origen, valor, fecha) "
                        "VALUES (?, ?, ?)",
                        registros
                    )

                self.enviar_json(201, {
                    "mensaje": "Lote guardado correctamente",
                    "eventos_guardados": len(registros)
                })

            # Se conserva la compatibilidad con un evento individual.
            elif isinstance(datos, dict):
                origen = str(datos["origen"])
                valor = float(datos["valor"])

                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute(
                        "INSERT INTO eventos (origen, valor, fecha) "
                        "VALUES (?, ?, ?)",
                        (origen, valor, fecha)
                    )

                self.enviar_json(201, {
                    "mensaje": "Evento guardado correctamente",
                    "eventos_guardados": 1
                })

            else:
                self.send_error(400, "Formato JSON incorrecto")

        except (
            ValueError, TypeError, KeyError, json.JSONDecodeError
        ):
            self.send_error(400, "Datos incorrectos")

    def log_message(self, formato, *args):
        print("%s - %s" % (
            self.address_string(), formato % args
        ))


if __name__ == "__main__":
    init_db()
    servidor = HTTPServer(("127.0.0.1", 8000), APIHandler)
    print("API disponible en http://127.0.0.1:8000")
    print("Admite eventos individuales y lotes.")
    print("Presiona Ctrl+C para detener el servidor")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.server_close()
