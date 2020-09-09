import csv
import os

from flask import Flask, request, send_file, render_template, flash, redirect, url_for
from io import BytesIO, StringIO
from vpg.VoucherPrint import VoucherPrint
import subprocess
import mysql.connector
from mysql.connector import errorcode
import tempfile
import itertools

PDFJAM_BIN = "/usr/bin/pdfjam"

VOUCHER_PRIVATE_KEY = os.environ['VOUCHER_PRIVATE_KEY']
VOUCHER_CFG = os.environ['VOUCHER_CFG']
VOUCHER_BIN = os.environ['VOUCHER_BIN']
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


def generate_vouchers(roll, count):
    roll_csv = subprocess.check_output(
        [VOUCHER_BIN, '-c', VOUCHER_CFG, '-p', VOUCHER_PRIVATE_KEY, str(roll), str(count)])

    vouchers_reader = csv.reader(StringIO(roll_csv.decode('utf-8')), delimiter=';', quotechar='"')
    vouchers = list(
        filter(lambda voucher: not voucher[0].startswith('#'), vouchers_reader))
    vouchers = [voucher[0].strip() for voucher in vouchers]

    return vouchers


def generate_buffer_pdf(roll, count):
    vouchers = generate_vouchers(roll, count)

    voucher_buffer = BytesIO()
    report = VoucherPrint(voucher_buffer, vouchers)
    report.print_vouchers()
    voucher_buffer.seek(0)
    return voucher_buffer, len(vouchers)


def buffer_pdf_to_2x2(voucher_buffer):
    process = subprocess.Popen([PDFJAM_BIN, "--nup", "2x2", "--outfile", "/dev/stdout", "--"], shell=False,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdoutdata, stderrdata = process.communicate(input=voucher_buffer.getvalue())

    if stderrdata is not None:
        return None, None

    return stdoutdata


def shuffle_ads(ads_file_path, voucher_pdf_path, voucher_pdf_pages):
    page_with_ads = 1

    pdfjam_pages = [
        [voucher_pdf_path, str(i + 1), ads_file_path,
         str(page_with_ads)] for i in range(voucher_pdf_pages)]

    process = subprocess.Popen(
        [PDFJAM_BIN, *list(itertools.chain(*pdfjam_pages)), "--outfile", "/dev/stdout", "--paper", "a4paper",
         "--rotateoversize",
         "false"],
        shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdoutdata, stderrdata = process.communicate()

    if stderrdata is not None:
        return None

    return stdoutdata


@app.route('/pdf/generate', methods=['POST'])
def pdf_generate():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    ads_file = request.files['ads_pdf']

    if ads_file.filename == '':
        flash("Error: Please provide an Ads file!")
        return redirect(url_for('home'))

    voucher_buffer, voucher_count = generate_buffer_pdf(roll, count)

    if voucher_buffer is None:
        flash("Error: Failed to generate 2x2 pdf!")
        return redirect(url_for('home'))

    with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix=".pdf") as ads_file_output:
        ads_file.save(ads_file_output)
        ads_file_output.flush()

        with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix=".pdf") as output:
            output.write(buffer_pdf_to_2x2(voucher_buffer))
            output.flush()

            final_pdf = shuffle_ads(ads_file_output.name, output.name, int(voucher_count / 4))  # /4 Because of 2x2 nup

            if final_pdf is None:
                flash("Error: Failed to shuffle ads!")
                return redirect(url_for('home'))

            return send_file(BytesIO(final_pdf),
                             mimetype='application/pdf',
                             as_attachment=True,
                             attachment_filename="vouchers_tatdf_roll%s.csv.pdf" % roll)


def activate_vouchers(cursor, vouchers):
    for voucher in vouchers:
        cursor.execute(
            "SELECT username FROM radcheck WHERE radcheck.username = %s;",
            (voucher,)
        )

        if len(cursor.fetchall()) == 0:
            cursor.execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s,'Max-All-Session',':=', %s);",
                (voucher, str(36 * 24 * 60 * 60))
            )

            cursor.execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s,'Cleartext-Password', ':=', 'dummy');",
                (voucher,)
            )
        else:
            return False

    return True


@app.route('/activation/step', methods=['POST'])
def activate_step():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    vouchers = generate_vouchers(roll, count)

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST"),
            user=os.environ.get("MYSQL_USER"),
            passwd=os.environ.get("MYSQL_PASSWORD"),
            option_files=[os.environ.get("MYSQL_OPTION_FILE")],
            database="radius"
        )
        connection.autocommit = False
        cursor = connection.cursor()

        if activate_vouchers(cursor, vouchers):
            connection.commit()
            flash("Successfully activated vouchers")
        else:
            flash("Error: Voucher already existed. Aborting!")
            connection.rollback()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            flash("Something is wrong with the database user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            flash("Database does not exist")
        else:
            flash("Something went wrong")
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

            if cursor is not None:
                cursor.close()

    return render_template('activation/step.html')
