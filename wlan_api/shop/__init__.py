from flask import Blueprint, jsonify, make_response, request
from flask import current_app

from wlan_api.generate import generate_vouchers

shop = Blueprint('shop', __name__)


# https://pythonise.com/series/learning-flask/working-with-json-in-flask


@shop.route('/', methods=["GET"])
def example():
    return jsonify({"message": "Request body must be JSON"}), 405


@shop.route('/getvoucher', methods=["GET"])
def example1():
    return make_response(jsonify({"message": "Request body must be JSON"}), 405)


@shop.route("/json", methods=["POST"])
def example2():
    if request.is_json:
        req = request.get_json()

        response_body = {
            "message": "JSON received!",
            "sender": req.get("name")
        }

        res = make_response(jsonify(response_body), 200)

        return res
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 405)


@shop.route("/vouchers", methods=["POST"])
def vouchers():
    if request.is_json:
        voucher_config = current_app.config['VOUCHER']
        vouchers = generate_vouchers(10, 100, voucher_config['key'],
                                     voucher_config['alphabet'],
                                     voucher_config['length'])
        res = make_response(jsonify(vouchers), 200)

        return res
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 405)
