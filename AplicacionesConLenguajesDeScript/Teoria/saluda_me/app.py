# Programacion Web

import flask
import sirope
from model.mensaje import Mensaje

def crea_app():
    app = flask.Flask(__name__)
    srp = sirope.Sirope()

    return app, srp
...

app, srp = crea_app()

@app.route("/")
def index():
    return flask.send_from_directory(app.static_folder, "index.html")

@app.route("/saludar", methods=["POST"])
def saludar():
    nombre = flask.request.form.get("edName")
    msg = flask.request.form.get("edMsg")

    if not msg:
        msg = "Soy muy timido"
    ...

    if not nombre:
        nombre = "Invitado"
    ...

    mensajes = list(srp.load_last(Mensaje, 10))

    m = Mensaje(nombre, msg)
    srp.save(m)

    sust = {
        "ultimo_mensaje": m,
        "mensajes": mensajes,
    }

    return flask.render_template("saludo.html", **sust)

if __name__ == "__main__":
    app.run(debug = True)