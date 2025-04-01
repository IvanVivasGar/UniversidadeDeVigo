from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/generar_factura", methods=["POST"])
def generar_factura():
    emisor = {
        "nombre": request.form["nombreEmisor"], "cif": request.form["cifEmisor"],
        "direccion": request.form["direccionEmisor"], "poblacion": request.form["poblacionEmisor"],
        "provincia": request.form["provinciaEmisor"], "cp": request.form["cpEmisor"],
        "pais": request.form["paisEmisor"], "contacto": request.form["contactoEmisor"],
        "email": request.form["emailEmisor"], "telefono": request.form["telefonoEmisor"]
    }

    cliente = {
        "nombre": request.form["nombreCliente"], "cif": request.form["cifCliente"],
        "direccion": request.form["direccionCliente"], "poblacion": request.form["poblacionCliente"],
        "provincia": request.form["provinciaCliente"], "cp": request.form["cpCliente"],
        "pais": request.form["paisCliente"], "contacto": request.form["contactoCliente"],
        "email": request.form["emailCliente"], "telefono": request.form["telefonoCliente"]
    }

    conceptos = request.form.getlist("concepto[]")
    precios = request.form.getlist("precio[]")
    unidades = request.form.getlist("unidades[]")
    unidad_tipo = request.form.getlist("unidad[]")
    ivas = request.form.getlist("iva[]")

    detalles = []
    total_factura = 0

    for i in range(len(conceptos)):
        precio = float(precios[i])
        unidad = int(unidades[i])
        iva = float(ivas[i])
        total = (precio * unidad) * (1 + iva / 100)

        detalles.append({
            "concepto": conceptos[i], "precio": precio, "unidades": unidad,
            "unidad": unidad_tipo[i], "iva": iva, "total": round(total, 2)
        })

        total_factura += total

    return render_template("factura.html", emisor=emisor, cliente=cliente, detalles=detalles, total_factura=round(total_factura, 2), fecha=datetime.now().strftime("%Y-%m-%d"))

if __name__ == "__main__":
    app.run(debug=True)