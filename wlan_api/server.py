import os
from flask import Flask

from wlan_api.shop import shop
from wlan_api.vpg import vpg

FLASK_SECRET = os.environ['FLASK_SECRET']


def create_app():
    app = Flask(__name__)
    app.secret_key = FLASK_SECRET

    app.register_blueprint(shop, url_prefix='/shop')
    app.register_blueprint(vpg, url_prefix='/vpg')
    return app
