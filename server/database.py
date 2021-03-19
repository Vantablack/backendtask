import psycopg2
import os
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=os.environ["PG_HOST"],
        database=os.environ["PG_DB"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"])


def get_server_version():
    """ Connect to the PostgreSQL database server and returns the server version"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()

        return db_version[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_all_customers(n_youngest=0):
    """ Connect to the PostgreSQL database server and returns all the customers"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # execute a statement
        if n_youngest > 0:
            cur.execute('SELECT * FROM "Customers" ORDER BY dob DESC LIMIT %s', (n_youngest,))
        else:
            cur.execute('SELECT * FROM "Customers" ORDER BY dob DESC')

        # display the PostgreSQL database server version
        all_customers = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()

        # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
        # return json.dumps(all_customers, default=default)
        return all_customers or []
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_one_customer(customer_id):
    """ Connect to the PostgreSQL database server and returns one customer"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # execute a statement
        cur.execute('SELECT * from "Customers" WHERE id=%s', (customer_id,))

        # display the PostgreSQL database server version
        one_customer = cur.fetchone()

        # close the communication with the PostgreSQL
        cur.close()

        # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
        return one_customer
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def insert_customer(name, dob):
    """ Connect to the PostgreSQL database server and insert a new customer"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # execute a statement
        sql_str = 'INSERT INTO "Customers" (name, dob) VALUES (%s, %s) RETURNING id'
        cur.execute(sql_str, (name, dob))
        new_id = cur.fetchone()['id']

        # commit the connection
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()

        return new_id

    except (Exception, psycopg2.DatabaseError) as error:
        print('error: {}'.format(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return


def check_customer_exists(customer_id):
    """ Connect to the PostgreSQL database server and check if the customer exists"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # execute a statement
        sql_str = 'SELECT id FROM "Customers" WHERE id=%s'
        cur.execute(sql_str, (customer_id,))

        # close the communication with the PostgreSQL
        cur.close()

        return cur.rowcount == 1

    except (Exception, psycopg2.DatabaseError) as error:
        print('error: {}'.format(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return


def update_customer(customer_id, name, dob):
    """ Connect to the PostgreSQL database server and update existing customer"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # execute a statement
        sql_str = 'UPDATE "Customers" SET (name, dob, updated_at) = (%s, %s, NOW()) WHERE id=%s'
        cur.execute(sql_str, (name, dob, customer_id))

        # commit the connection
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print('error: {}'.format(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return


def delete_customer(customer_id):
    """ Connect to the PostgreSQL database server and delete existing customer"""
    conn = None

    try:
        conn = get_connection()

        # create a cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # execute a statement
        sql_str = 'DELETE FROM "Customers" WHERE id=%s'
        cur.execute(sql_str, (customer_id,))

        # commit the connection
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print('error: {}'.format(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return
