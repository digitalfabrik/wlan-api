import csv
import os

from flask import Flask, request, send_file, render_template, flash, redirect
from io import BytesIO, StringIO
from vpg.VoucherPrint import VoucherPrint
import subprocess
import mysql.connector
from mysql.connector import errorcode
import tempfile
import itertools

VOUCHER_PRIVATE_KEY = os.environ['VOUCHER_PRIVATE_KEY']
VOUCHER_CFG = os.environ['VOUCHER_CFG']
VOUCHER_BIN = os.environ['VOUCHER_BIN']

app = Flask(__name__)


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


@app.route('/pdf/generate', methods=['POST'])
def pdf_generate():
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    ads_file = request.files['ads_pdf']

    if ads_file.filename == '':
        return 'bad request!', 400

    vouchers = generate_vouchers(roll, count)

    voucher_buffer = BytesIO()

    report = VoucherPrint(voucher_buffer, vouchers)
    report.print_vouchers()
    voucher_buffer.seek(0)

    with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix=".pdf") as ads_file_output:
        ads_file.save(ads_file_output)
        # ads_file_output.close()

        with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix=".pdf") as output:
            process = subprocess.Popen(["/usr/bin/pdfjam", "--nup", "2x2", "--outfile", "/dev/stdout", "--"], shell=False,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdoutdata, stderrdata = process.communicate(input=voucher_buffer.getvalue())
            output.write(stdoutdata)
            # output.close()

            voucher_pages = int(len(vouchers) / 4)  # Because of 2x2 nup
            page_with_ads = 1

            pdfjam_pages = [
                [output.name, str(i + 1), ads_file_output.name,
                 str(page_with_ads)] for i in range(voucher_pages)]

            process = subprocess.Popen(
                ["/usr/bin/pdfjam", *list(itertools.chain(*pdfjam_pages)), "--outfile", "/dev/stdout", "--paper", "a4paper", "--rotateoversize",
                 "false"],
                shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdoutdata, stderrdata = process.communicate(input=stdoutdata)

    return send_file(BytesIO(stdoutdata),
                     mimetype='application/pdf',
                     as_attachment=True,
                     attachment_filename="vouchers_tatdf_roll%s.csv.pdf" % roll)


@app.route('/activation/step', methods=['POST'])
def activate_step():
    message = "Successfully activated vouchers"
    roll = int(request.form['roll'])
    count = int(request.form['count'])
    vouchers = generate_vouchers(roll, count)

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

                print("Activating voucher\t%s" % voucher)
            else:
                print("Skipping voucher\t%s" % voucher)

        connection.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            message = "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            message = "Database does not exist"
        else:
            message = "Something went wrong"
    finally:
        if connection != None and connection.is_connected():
            connection.close()
            cursor.close()

    return render_template('activation/step.html', message=message)
