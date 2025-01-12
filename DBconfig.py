import mysql.connector

import logging

# Database configuration (use environment variables for security in a production environment)

import mysql.connector
import logging

# Database configuration (use environment variables for security in a production environment)
logging.basicConfig(level=logging.INFO)


def get_db_connection():
    """
    Establishes a connection to the MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection object if successful, 
                                                     otherwise None.
    """
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="your_username",
            password="your_password", 
            database="db_name", 
            auth_plugin="mysql_native_password"  # Use mysql_native_password 
        )
        logging.info("Successfully connected to the database.")
        return mydb

    except mysql.connector.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        return None
