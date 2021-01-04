from os import environ
from typing import Dict
import json
from itertools import cycle
from time import sleep
from uuid import uuid1

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


@app.route("/speech/say", methods=["POST"])
def speech_say():
    body = request.json
    phrase = body['phrase']
    redis_client.publish("subsystem.speech.command", phrase)
    return json.dumps({})


@app.route("/listen/phrase", methods=["POST"])
def listen_phrase():
    pubsub.subscribe("subsystem.listener.recordings")
    request_id = str(uuid1())
    message = {
        "request_id": request_id,
        "mode": "phrase"
    }
    redis_client.publish("subsystem.listener.command", json.dumps(message))
    while cycle([True]):
        redis_message = pubsub.get_message()
        if redis_message is not None:
            message = json.loads(redis_message['data'])
            if message['request_id'] == request_id:
                return json.dumps({
                    "wav_file": message['wav_file'],
                    "transcription": message['transcription']
                })
            sleep(0.1)


app.run(host=config['server']['address'], port=config['server']['port'], debug=config['server']['debug'])