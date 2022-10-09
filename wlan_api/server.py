import os

from flask import Flask

from wlan_api.vpg import vpg
import yaml
import pathlib


def create_app():
    app = Flask(__name__)

    pathlib.Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    config_file = app.instance_path + "/config.yml"

    if not pathlib.Path(config_file).exists():
        raise Exception("Unable to find config")

    app.config.from_file(config_file, load=lambda f: yaml.load(f, Loader=yaml.CLoader))

    app.register_blueprint(vpg, url_prefix='/vpg')
    return app
