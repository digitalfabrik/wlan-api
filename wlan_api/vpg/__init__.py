from flask import Blueprint, current_app
from flask import request, send_file, render_template, flash, redirect, url_for
from io import BytesIO

from wlan_api.activation import insert_vouchers_into_database
from wlan_api.generate import generate_vouchers
from wlan_api.pdf import VoucherPrint

from wlan_api.pdf.pdfjam import merge_final_pdf

vpg = Blueprint('vpg', __name__, static_folder='static', template_folder='templates')

ROLL_MAX = 65535   # 2-byte little-endian unsigned cap (HMAC encoding contract)
COUNT_MAX = 1000   # realistic batch <= 600; some headroom


def _parse_roll_count(form):
    """Return (roll, count) parsed from a request form.

    Raises ValueError with a user-facing German message on invalid input.
    """
    try:
        roll = int(form['roll'])
        count = int(form['count'])
    except (KeyError, ValueError, TypeError):
        raise ValueError("Roll und Anzahl müssen ganze Zahlen sein.")
    if not 0 <= roll <= ROLL_MAX:
        raise ValueError(f"Roll muss zwischen 0 und {ROLL_MAX} liegen.")
    if not 1 <= count <= COUNT_MAX:
        raise ValueError(f"Anzahl muss zwischen 1 und {COUNT_MAX} liegen.")
    return roll, count


def _reject_invalid_input(err):
    """Log the offending input and bounce the user back to the home page."""
    current_app.logger.warning(
        "Rejected /vpg input from %s: roll=%r count=%r (%s)",
        request.remote_addr,
        request.form.get('roll'),
        request.form.get('count'),
        err,
    )
    flash(f"Fehler: {err}")
    return redirect(url_for('vpg.home'))


@vpg.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@vpg.route('/pdf/step', methods=['POST'])
def pdf_step():
    try:
        roll, count = _parse_roll_count(request.form)
    except ValueError as err:
        return _reject_invalid_input(err)
    return render_template('pdf/step.html', roll=roll, count=count)


def create_pdf_buffer(vouchers, validity_days):
    voucher_buffer = BytesIO()
    report = VoucherPrint(voucher_buffer, vouchers, validity_days)
    report.print_vouchers()
    voucher_buffer.seek(0)
    return voucher_buffer, len(vouchers)


@vpg.route('/pdf/generate', methods=['POST'])
def pdf_generate():
    try:
        roll, count = _parse_roll_count(request.form)
    except ValueError as err:
        return _reject_invalid_input(err)

    ads_file = request.files['ads_pdf']

    if ads_file.filename == '':
        flash("Error: Please provide an Ads file!")
        return redirect(url_for('vpg.home'))

    voucher_config = current_app.config['VOUCHER']
    vouchers = generate_vouchers(roll, count, voucher_config['key'],
                                 voucher_config['alphabet'],
                                 voucher_config['length'])
    voucher_buffer, voucher_count = create_pdf_buffer(vouchers, voucher_config['validity_days'])

    if voucher_buffer is None:
        flash("Error: Failed to generate pdf!")
        return redirect(url_for('vpg.home'))

    final_pdf = merge_final_pdf(voucher_buffer, voucher_count, ads_file)

    if final_pdf is None:
        flash("Error: Failed to shuffle ads!")
        return redirect(url_for('vpg.home'))

    return send_file(BytesIO(final_pdf),
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name="vouchers_tatdf_roll%s.csv.pdf" % roll)


@vpg.route('/activation/step', methods=['POST'])
def activate_step():
    try:
        roll, count = _parse_roll_count(request.form)
    except ValueError as err:
        return _reject_invalid_input(err)

    voucher_config = current_app.config['VOUCHER']
    vouchers = generate_vouchers(roll, count, voucher_config['key'],
                                 voucher_config['alphabet'],
                                 voucher_config['length'])

    flash(insert_vouchers_into_database(vouchers, current_app.config['MYSQL'], voucher_config))

    return render_template('activation/step.html')
