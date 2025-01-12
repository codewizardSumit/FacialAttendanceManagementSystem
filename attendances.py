import logging
from datetime import datetime
from biometric_utils import find_person_by_biometric, is_match
from DBconfig import get_db_connection

############################_THIS FILE IS USED FOR ATTENDANCE OF STUDENTS DURING CLASS_#########################################
# Initialize logging
logging.basicConfig(level=logging.INFO)

def choose_person_type():
    """
    Display a menu to choose whether the person is a Teacher or Student.
    
    Returns:
        str: The chosen person type ('teacher' or 'student').
    """
    while True:
        print("Please choose the person type:")
        print("1. Teacher")
        print("2. Student")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == '1':
            return 'teacher'
        elif choice == '2':
            return 'student'
        else:
            print("Invalid choice, please select 1 for Teacher or 2 for Student.")



def record_attendance(session_id, enrollment_id, biometric_data, attendance_status='present', excuse_reason_id=None):
    """
    Record attendance for a student.

    Args:
        session_id (int): The session ID.
        enrollment_id (int): The enrollment ID of the student.
        biometric_data (bytes): Biometric data to verify the student.
        attendance_status (str): Attendance status ('present', 'absent', 'late', 'excused').
        excuse_reason_id (int, optional): Reason ID for excused absences.
    """
    db = get_db_connection()
    if db is None:
        logging.error("Database connection failed. Attendance not recorded.")
        return

    try:
        cursor = db.cursor()

        # Verify the biometric data matches the student
        if enrollment_id and is_match(biometric_data, enrollment_id):
            # Prepare query based on provided columns
            if excuse_reason_id:
                query = """
                    INSERT INTO attendances (session_id, enrollment_id, excuse_reason_id, attendance_status)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (session_id, enrollment_id, excuse_reason_id, attendance_status))
            else:
                query = """
                    INSERT INTO attendances (session_id, enrollment_id, attendance_status)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (session_id, enrollment_id, attendance_status))

            # Commit the transaction
            db.commit()
            logging.info(f"Attendance recorded for Enrollment ID: {enrollment_id} with status '{attendance_status}'.")
            print(f"Attendance successfully recorded for Enrollment ID: {enrollment_id} with status '{attendance_status}'.")
        else:
            logging.warning(f"No matching student found for Enrollment ID: {enrollment_id}.")
            print("Attendance not recorded: No matching student found.")

    except Exception as e:
        logging.error(f"Error while recording attendance: {str(e)}")
        db.rollback()  # Rollback the transaction in case of error
    finally:
        try:
            cursor.close()
        except Exception as close_error:
            logging.error(f"Error closing cursor: {str(close_error)}")
        try:
            db.close()
        except Exception as close_error:
            logging.error(f"Error closing database connection: {str(close_error)}")
