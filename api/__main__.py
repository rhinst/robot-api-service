from os import environ
from typing import Dict
import json

from flask import Flask
from redis import Redis
from redis.client import PubSub

from api.config import load_config

environment: str = environ.get("ENVIRONMENT", "dev")
config: Dict = load_config(environment)
redis: Redis = Redis(host=config["redis"]["host"], port=config["redis"]["port"], db=0)
pubsub: PubSub = redis.pubsub()
app: Flask = Flask(__name__)


@app.route("/sonar/distance")
def get_sonar_distance():
    pubsub.subscribe("subsystem.sonar")
    redis_message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
    if redis_message is None:
        return json.dumps({
            "error": "No response from sonar device."
        }), 500
    message = json.loads(redis_message)
    return json.dumps({
        "distance": message["data"]
    })


app.run(host=config['server']['address'], port=config['server']['port'], debug=config['server']['debug'])