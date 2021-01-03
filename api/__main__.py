from os import environ
from typing import Dict
import json

from flask import Flask, request, render_template
from redis import Redis
from redis.client import PubSub

from api.config import load_config

environment: str = environ.get("ENVIRONMENT", "dev")
config: Dict = load_config(environment)
redis_client: Redis = Redis(host=config["redis"]["host"], port=config["redis"]["port"], db=0)
pubsub: PubSub = redis_client.pubsub()
app: Flask = Flask(__name__, template_folder="templates")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/sonar/distance")
def get_sonar_distance():
    pubsub.subscribe("subsystem.sonar.measurement")
    redis_message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
    pubsub.unsubscribe()
    if redis_message is None:
        return json.dumps({
            "error": "No response from sonar device."
        }), 500
    message = json.loads(redis_message)
    return json.dumps({
        "distance": message["data"]
    })


@app.route("/motor/drive", methods=["POST"])
def motor_drive():
    body = request.json
    speed = float(body['speed']) if 'speed' in body else 1.0
    direction = body['direction'] if 'direction' in body else 'forward'
    message = {
       "command": "drive",
       "speed": speed,
       "direction": direction
    }
    redis_client.publish("subsystem.motor.command", json.dumps(message))
    return json.dumps({})


@app.route("/motor/stop", methods=["POST"])
def motor_stop():
    message = {
        "command": "stop"
    }
    redis_client.publish("subsystem.motor.command", json.dumps(message))
    return json.dumps({})


app.run(host=config['server']['address'], port=config['server']['port'], debug=config['server']['debug'])