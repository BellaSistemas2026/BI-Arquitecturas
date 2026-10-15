
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
    def do_GET(self):
        if self.path == "/":
            respuesta = {
                "proyecto": "BI Arquitecturas",
                "estado": "funcionando",
                "base_datos": DB_NAME
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

        elif self.path == "/eventos":
            with sqlite3.connect(DB_NAME) as conn:
                filas = conn.execute(
                    "SELECT id, origen, valor, fecha FROM eventos ORDER BY id DESC"
                ).fetchall()

            respuesta = [
                {"id": f[0], "origen": f[1], "valor": f[2], "fecha": f[3]}
                for f in filas
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

        else:
            self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        if self.path != "/eventos":
            self.send_error(404, "Ruta no encontrada")
            return

        try:
            longitud = int(self.headers.get("Content-Length", 0))
            datos = json.loads(self.rfile.read(longitud).decode("utf-8"))

            origen = str(datos["origen"])
            valor = float(datos["valor"])
            fecha = time.time()

            with sqlite3.connect(DB_NAME) as conn:
                conn.execute(
                    "INSERT INTO eventos (origen, valor, fecha) VALUES (?, ?, ?)",
                    (origen, valor, fecha)
                )

            respuesta = {"mensaje": "Evento guardado correctamente"}
            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

        except (ValueError, KeyError, json.JSONDecodeError):
            self.send_error(400, "Datos incorrectos")

    def log_message(self, formato, *args):
        print("%s - %s" % (self.address_string(), formato % args))


if __name__ == "__main__":
    init_db()
    servidor = HTTPServer(("127.0.0.1", 8000), APIHandler)
    print("API disponible en http://127.0.0.1:8000")
    print("Presiona Ctrl+C para detener el servidor")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
        servidor.server_close()
