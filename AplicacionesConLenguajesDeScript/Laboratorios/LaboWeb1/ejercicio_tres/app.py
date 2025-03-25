import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.send_from_directory(app.static_folder, "index.html")

@app.route("/resultado", methods=["POST"])
def resultado():
    numero = flask.request.form.get("edNumero")
    try:
        numero = int(numero)
    except (TypeError, ValueError):
        numero = 0

    return """
        <!DOCType html>
        <html>
            <head><title>Resultado</title></head>
            <body>
                <h1>Grados Farenheit: $celsius</h1>
                <h1>Grados Celsius: $farenheit</h1>
            </body>
        </html>
    """.replace("$celsius", str(((numero * 9) / 5) + 32)).replace("$farenheit", str((numero - 32) * 0.555))