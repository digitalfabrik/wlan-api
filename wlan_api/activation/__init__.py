import mysql
from mysql.connector import errorcode


def insert_vouchers_into_database(vouchers, mysql_config):
    host = mysql_config['host']
    user = mysql_config['user']
    password = mysql_config['password']
    optionfile = mysql_config.get('option-file')

    message = None
    connection = None
    cursor = None

    try:
        additional_args = {}

        if optionfile is not None:
            additional_args['option_files'] = optionfile

        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
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


