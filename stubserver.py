import json

import flask
from flask import Flask, abort, request

app = Flask(__name__)


@app.route("/foo")
def foo():
    return "Barrrr"


@app.route("/foo/1")
def foo_1():
    flask.abort(404)


@app.route("/foo/2")
def foo_2():
    return json.dumps({"foo": 2, "bar": False})


@app.route("/kv/pyrandall/avro_ok")
def kv_avro_ok():
    return json.dumps({"Avro": "ok"})


# test assertions
@app.route("/foo/bar/123")
def foo_bar_123_response_200():
    return json.dumps({"hello": "world"})


# simulator posts to /users
@app.route("/users", methods=["POST"])
def users_post():
    if len(request.data) == 0:
        abort(400)
    return "", 201


@app.route("/v1/actions/produce-event", methods=["POST"])
def schema_ingest_actions_produce():
    if len(request.data) == 0:
        abort(400)
    if request.headers.get("event-type", "") == "avro.bad":
        return "", 400
    return "", 204


if __name__ == "__main__":
    app.run()
