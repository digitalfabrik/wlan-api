import os

from flask import Flask, request, send_file, render_template, flash, redirect, url_for
from io import BytesIO

from wlan_api.activation import insert_vouchers_into_database
from wlan_api.generate import generate_vouchers_pfsense
from wlan_api.pdf import VoucherPrint

from wlan_api.pdf.pdfjam import merge_final_pdf

FLASK_SECRET = os.environ['FLASK_SECRET']

app = Flask(__name__)
app.secret_key = FLASK_SECRET


def create_app():
    return app


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/pdf/step', methods=['POST'])
def pdf_step():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    return render_template('pdf/step.html', roll=roll, count=count)


def create_pdf_buffer(vouchers):
    voucher_buffer = BytesIO()
    report = VoucherPrint(voucher_buffer, vouchers)
    report.print_vouchers()
    voucher_buffer.seek(0)
    return voucher_buffer, len(vouchers)


@app.route('/pdf/generate', methods=['POST'])
def pdf_generate():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    ads_file = request.files['ads_pdf']

    if ads_file.filename == '':
        flash("Error: Please provide an Ads file!")
        return redirect(url_for('home'))

    vouchers = generate_vouchers_pfsense(roll, count)
    voucher_buffer, voucher_count = create_pdf_buffer(vouchers)

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
                     attachment_filename="vouchers_tatdf_roll%s.csv.pdf" % roll)


@app.route('/activation/step', methods=['POST'])
def activate_step():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    vouchers = generate_vouchers_pfsense(roll, count)

    flash(insert_vouchers_into_database(vouchers))

    return render_template('activation/step.html')
