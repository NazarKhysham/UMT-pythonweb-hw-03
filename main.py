import json
import mimetypes
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
DATA_FILE = STORAGE_DIR / "data.json"


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_html("index.html")

        elif self.path == "/message":
            self.send_html("message.html")

        elif self.path == "/read":
            self.send_read_page()

        elif self.path in ["/style.css", "/logo.png"]:
            self.send_static_file(self.path[1:])

        else:
            self.send_html("error.html", status=404)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            form_data = parse_qs(body)

            username = form_data.get("username", [""])[0]
            message = form_data.get("message", [""])[0]

            self.save_message(username, message)

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_html("error.html", status=404)

    def send_html(self, filename, status=200):
        file_path = BASE_DIR / filename

        if not file_path.exists():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def send_static_file(self, filename):
        file_path = BASE_DIR / filename

        if not file_path.exists():
            self.send_html("error.html", status=404)
            return

        content_type, _ = mimetypes.guess_type(file_path)

        self.send_response(200)
        self.send_header("Content-type", content_type or "application/octet-stream")
        self.end_headers()

        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def save_message(self, username, message):
        STORAGE_DIR.mkdir(exist_ok=True)

        if not DATA_FILE.exists():
            DATA_FILE.write_text("{}", encoding="utf-8")

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

        data[str(datetime.now())] = {
            "username": username,
            "message": message
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        def send_read_page(self):
            STORAGE_DIR.mkdir(exist_ok=True)

        if not DATA_FILE.exists():
            DATA_FILE.write_text("{}", encoding="utf-8")

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

        env = Environment(loader=FileSystemLoader(BASE_DIR))
        template = env.get_template("read.html")
        html = template.render(messages=data)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))



def run():
    server = HTTPServer(("localhost", 3000), MyHandler)
    print("Server started at http://localhost:3000")
    server.serve_forever()


if __name__ == "__main__":
    run()