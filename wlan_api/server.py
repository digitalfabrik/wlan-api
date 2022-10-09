from flask import Flask

from wlan_api.vpg import vpg
import yaml


def create_app():
    app = Flask(__name__)
    app.config.from_file("../config.yml", load=lambda f: yaml.load(f, Loader=yaml.CLoader))

    app.register_blueprint(vpg, url_prefix='/vpg')
    return app
