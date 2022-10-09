from flask import Blueprint, current_app
from flask import request, send_file, render_template, flash, redirect, url_for
from io import BytesIO

from wlan_api.activation import insert_vouchers_into_database
from wlan_api.generate import generate_vouchers
from wlan_api.pdf import VoucherPrint

from wlan_api.pdf.pdfjam import merge_final_pdf

vpg = Blueprint('vpg', __name__, static_folder='static', template_folder='templates')


@vpg.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@vpg.route('/pdf/step', methods=['POST'])
def pdf_step():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    return render_template('pdf/step.html', roll=roll, count=count)


def create_pdf_buffer(vouchers, validity_days):
    voucher_buffer = BytesIO()
    report = VoucherPrint(voucher_buffer, vouchers, validity_days)
    report.print_vouchers()
    voucher_buffer.seek(0)
    return voucher_buffer, len(vouchers)


@vpg.route('/pdf/generate', methods=['POST'])
def pdf_generate():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
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
        return redirect(url_for('home'))

    final_pdf = merge_final_pdf(voucher_buffer, voucher_count, ads_file)

    if final_pdf is None:
        flash("Error: Failed to shuffle ads!")
        return redirect(url_for('home'))

    return send_file(BytesIO(final_pdf),
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name="vouchers_tatdf_roll%s.csv.pdf" % roll)


@vpg.route('/activation/step', methods=['POST'])
def activate_step():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    voucher_config = current_app.config['VOUCHER']
    vouchers = generate_vouchers(roll, count, voucher_config['key'],
                                 voucher_config['alphabet'],
                                 voucher_config['length'])

    flash(insert_vouchers_into_database(vouchers, current_app.config['MYSQL'], voucher_config))

    return render_template('activation/step.html')
