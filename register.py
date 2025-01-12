import mysql.connector
import logging
import re
from getMeanEncodings import capture_and_extract_mean_encoding
from mysql.connector import Error, IntegrityError
from DBconfig import get_db_connection
import numpy as np
import pickle

# Initialize logging
logging.basicConfig(filename='registration.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to validate email format
def is_valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(regex, email)

# Function to validate date of birth format (YYYY-MM-DD)
def is_valid_date(date):
    regex = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(regex, date)

# Function to validate course ID (if provided)
def is_valid_course_id(course_id):
    return course_id.isdigit()

# Function to check for duplicate email
def is_duplicate_email(email, table_name):
    db = get_db_connection()
    if db is None:
        logging.error("Failed to connect to database.")
        return True
    
    try:
        with db.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE LOWER(email) = LOWER(%s)", (email,))
            result = cursor.fetchone()
            return result[0] > 0
    except Error as e:
        logging.error(f"Error while checking for duplicate email: {e}")
        return True
    finally:
        db.close()

# Function to register a teacher
def register_teacher():
    teacher_id = int(input("Enter Teacher ID: "))
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    
    gender = input("Enter gender (Male, Female, Other): ")
    if gender not in ('Male','male' , 'Female','female', 'Other','other'):
        print("Invalid gender selection.")
        return

    date_of_birth = input("Enter date of birth (YYYY-MM-DD): ")
    if not is_valid_date(date_of_birth):
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    email = input("Enter email: ")
    if not is_valid_email(email):
        print("Invalid email format.")
        return

    if is_duplicate_email(email, 'teachers'):
        print("A teacher with this email already exists.")
        return

    phone_number = input("Enter phone number: ")
    address = input("Enter address: ")

    query = """INSERT INTO teachers (teacher_id, first_name, last_name, gender, date_of_birth, email, 
               phone_number, address, biometric_data) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    register_person((teacher_id, first_name, last_name, gender, date_of_birth, email, phone_number, address), query)

# Function to register a student
def register_student():
    enrollment_id = int(input("Enter Enrolment ID: "))
    course_id = input("Enter course ID: ").strip()
    if course_id and not is_valid_course_id(course_id):
        print("Invalid course ID. Please enter a valid numeric ID.")
        return
    course_id = int(course_id) if course_id else None

    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    
    gender = input("Enter gender (Male, Female, Other): ")
    if gender not in ('Male','male' , 'Female','female', 'Other','other'):
        print("Invalid gender selection.")
        return

    date_of_birth = input("Enter date of birth (YYYY-MM-DD): ")
    if not is_valid_date(date_of_birth):
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    email = input("Enter email: ")
    if not is_valid_email(email):
        print("Invalid email format.")
        return

    if is_duplicate_email(email, 'students'):
        print("A student with this email already exists.")
        return

    phone_number = input("Enter phone number: ")
    address = input("Enter address: ")

    query = """INSERT INTO students (enrollment_id, course_id, first_name, last_name, gender, date_of_birth, 
               email, phone_number, address, biometric_data) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    register_person((enrollment_id, course_id, first_name, last_name, gender, date_of_birth, email, phone_number, address), query)

# Generic function to register a person in the database
def register_person(fields, query):
    print("Please look at the camera for biometric data...")

    biometric_data = capture_and_extract_mean_encoding()  # Capture biometric data

    if biometric_data is None:
        logging.error("Face detection failed. Registration aborted.")
        return

    # Convert biometric data to a pickled format before saving to the database
    if isinstance(biometric_data, np.ndarray):
        biometric_data = pickle.dumps(biometric_data)  # Pickle the numpy array

    db = get_db_connection()
    if db is None:
        logging.error("Database connection failed. Registration aborted.")
        return

    try:
        with db.cursor() as cursor:
            cursor.execute(query, fields + (biometric_data,))
            db.commit()
            logging.info("Registered successfully.")
            print("Registration successful!")
    except IntegrityError as e:
        if "Duplicate entry" in str(e):
            logging.error("The provided email or biometric data already exists.")
            print("Registration failed: Duplicate entry.")
        else:
            logging.error(f"Integrity error occurred: {e}")
            print("Registration failed due to an integrity error.")
        db.rollback()
    except Error as e:
        logging.error(f"Error while saving data: {e}")
        print("An error occurred while saving data.")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    print("Select Registration Type:")
    print("[1]. Teacher")
    print("[2]. Student")
    
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                register_teacher()
            elif choice == 2:
                register_student()
            else:
                print("Invalid input. Please try again.")
            break  # Exit the loop after valid input
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            logging.info("Program interrupted by user.")
            break
