import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.send_from_directory(app.static_folder, "index.html")