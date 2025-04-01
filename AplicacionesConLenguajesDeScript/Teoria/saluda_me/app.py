# Programacion Web

import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.send_from_directory(app.static_folder, "index.html")

@app.route("/saludar", methods=["POST"])
def saludar():
    nombre = flask.request.form.get("edName")
    if not nombre:
        nombre = "Invitado"
    ...

    sust = {
        "name": nombre,
        "primos": ()
    }

    return flask.render_template("saludo.html", **sust)

if __name__ == "__main__":
    app.run(debug = True)