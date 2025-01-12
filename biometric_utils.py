import mysql.connector
import logging
from DBconfig import get_db_connection
from typing import Optional
import face_recognition
import pickle
import numpy as np

def find_person_by_biometric(biometric_data: bytes, person_type: str, threshold: float = 0.6) -> Optional[int]:
    """
    Find a person (student or teacher) in the database using their biometric data.

    Args:
        biometric_data (bytes): The biometric data (face encoding) to search for.
        person_type (str): The type of person to search for ('student' or 'teacher').
        threshold (float): The distance threshold for face recognition comparison.

    Returns:
        Optional[int]: The ID of the matching person, or None if not found.
    """
    if biometric_data is None:
        logging.warning("No biometric data provided.")
        return None

    db = None
    cursor = None
    try:
        db = get_db_connection()
        if db is None:
            logging.error("Database connection failed.")
            return None
        cursor = db.cursor()

        if person_type == 'student':
            query = "SELECT enrollment_id, biometric_data FROM students"
        elif person_type == 'teacher':
            query = "SELECT teacher_id, biometric_data FROM teachers"
        else:
            logging.error("Invalid person type specified. Must be 'student' or 'teacher'.")
            return None

        cursor.execute(query)
        persons = cursor.fetchall()

        for person_id, stored_biometric_data in persons:
            stored_biometric_data = pickle.loads(stored_biometric_data)
            matches = face_recognition.compare_faces([stored_biometric_data], biometric_data)
            distance = face_recognition.face_distance([stored_biometric_data], biometric_data)

            if matches[0] and distance[0] < threshold:
                logging.info(f"{person_type.capitalize()} found with ID: {person_id}")
                return person_id

        logging.info(f"No matching {person_type} found with the provided biometric data.")
        return None

    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()




def is_match(biometric_data: bytes, person_id: str) -> bool:
    """
    Check if the captured biometric data matches the saved data in the database.
    
    Args:
        biometric_data (bytes): The captured biometric data (face encoding).
        person_id (str): The ID of the student (enrollment_id).

    Returns:
        bool: True if a match is found, False otherwise.
    """
    db = get_db_connection()
    if db is None:
        logging.error("Database connection failed for matching.")
        return False

    try:
        cursor = db.cursor()

        # Query to get the pickled biometric data for the student
        query = "SELECT biometric_data FROM students WHERE enrollment_id = %s"
        
        cursor.execute(query, (person_id,))
        result = cursor.fetchone()

        if result:
            # Unpickle the stored biometric data
            saved_biometric_data = pickle.loads(result[0])

            # Ensure the captured biometric data is in the correct format for comparison
            input_biometric_data = np.frombuffer(biometric_data, dtype=np.float64)

            # Ensure both inputs have the same length
            if saved_biometric_data.size != input_biometric_data.size:
                logging.error("Biometric data size mismatch between stored and captured data.")
                return False

            # Compare the saved data with the input data
            match_result = face_recognition.compare_faces([saved_biometric_data], input_biometric_data)

            if match_result[0]:
                logging.info(f"Biometric match found for student with ID: {person_id}.")
                return True
            else:
                logging.warning(f"No match found for student with ID: {person_id}.")
                return False
        else:
            logging.warning(f"No biometric data found in the database for student ID: {person_id}.")
            return False

    except Exception as e:
        logging.error(f"Error while checking biometric match: {e}")
        return False
    finally:
        try:
            cursor.close()
        except Exception as close_error:
            logging.error(f"Error closing cursor: {str(close_error)}")
        try:
            db.close()
        except Exception as close_error:
            logging.error(f"Error closing database connection: {str(close_error)}")
