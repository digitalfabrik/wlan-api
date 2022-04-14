import os

import mysql
from mysql.connector import errorcode


MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
MYSQL_OPTION_FILE = os.environ.get('MYSQL_OPTION_FILE')


def insert_vouchers_into_database(vouchers):
    message = None
    connection = None
    cursor = None

    try:
        additional_args = {}

        if MYSQL_OPTION_FILE is not None:
            additional_args['option_files'] = MYSQL_OPTION_FILE

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database="radius",
            *additional_args
        )

        connection.autocommit = False
        cursor = connection.cursor()

        if activate_vouchers(cursor, vouchers):
            connection.commit()
            message = "Successfully activated vouchers"
        else:
            connection.rollback()
            message = "Error: Voucher already existed. Aborting!"

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            message = "Something is wrong with the database user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            message = "Database does not exist"
        else:
            message = "Something went wrong"
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

            if cursor is not None:
                cursor.close()

    return message


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


