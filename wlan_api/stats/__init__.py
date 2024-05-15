from flask import Blueprint, current_app, make_response
from flask import request, send_file, render_template, flash, redirect, url_for
from io import BytesIO
import mysql
from mysql.connector import errorcode


stats = Blueprint('stats', __name__, static_folder='static', template_folder='templates')

@stats.route('/', methods=['GET'])
def home():
    mysql_config = current_app.config['MYSQL']
    host = mysql_config['host']
    user = mysql_config['user']
    password = mysql_config['password']
    optionfile = mysql_config.get('option-file')

    message = None
    connection = None
    cursor = None

    output = None
    try:
        additional_args = {}

        if optionfile is not None:
            additional_args['option_files'] = optionfile

        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database="radius",
            **additional_args
        )

        cursor = connection.cursor()

        cursor.execute('WITH USER_FIRST AS (   SELECT username, min(acctstarttime) as acctstarttime   FROM radacct   GROUP BY username ) SELECT   EXTRACT(YEAR FROM acctstarttime) AS year,   EXTRACT(MONTH FROM acctstarttime) AS month,   COUNT(username) AS user_count FROM   USER_FIRST GROUP BY   EXTRACT(YEAR FROM acctstarttime),   EXTRACT(MONTH FROM acctstarttime) ORDER BY year,   month;').fetchall()
        output = cursor.fetchall()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            message = "Something is wrong with the database user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            message = "Database does not exist"
        else:
            print(err)
            message = "Something went wrong"
            raise err
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

            if cursor is not None:
                cursor.close()

    text = ""

    for year, month, count in output:
        text += f"{year}, {month} - {count}\n"

    response = make_response(text, 200)
    response.mimetype = "text/plain"

    return message if message is not None else response

