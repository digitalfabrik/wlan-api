import os
import pathlib

import yaml
from flask import Flask, redirect

from wlan_api.vpg import vpg


def create_app():
    app = Flask("wlan-api")

    pathlib.Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    config_file = app.instance_path + "/config.yml"

    print("Config: " + config_file)

    if not pathlib.Path(config_file).exists():
        raise Exception("Unable to find config")

    app.config.from_file(config_file, load=lambda f: yaml.load(f, Loader=yaml.CLoader))

    @app.route('/', methods=['GET'])
    def home():
        return redirect('/vpg')

    app.register_blueprint(vpg, url_prefix='/vpg')

    return app
