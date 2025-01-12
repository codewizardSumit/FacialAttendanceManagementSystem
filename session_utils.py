import datetime
import logging
from DBconfig import get_db_connection
from attendances import record_attendance, choose_person_type
from biometric_utils import find_person_by_biometric
from classUtils import select_class
from getCurrentEncodings import capture_and_extract_encoding

# Constants for user prompts
EXIT_PROMPT = "Press 'Enter' to continue or type 'exit' to finish the session: "
SESSION_END_PROMPT = "Ending the attendance session..."
ATTENDANCE_SUCCESS = "Attendance recorded for {} ID: {}"
ATTENDANCE_FAIL = "No matching student or teacher found. Please try again."
FAILED_CAPTURE_PROMPT = "Failed to capture biometric data. Please try again."
TEACHER_VERIFICATION_FAIL = "Teacher biometric verification failed. Cannot close session."

def log_attendance(session_id, student_id, status):
    logging.info(f"Session ID: {session_id}, Student ID: {student_id}, Status: {status}")




# handle attendance session function
def handle_attendance_session():
    print("General Info: To start class, a teacher needs to initiate a class session first.\n")

    # Teacher selects the person type for the session
    person_type = choose_person_type()
    if person_type != "teacher":
        print("Error: Only a teacher can initiate a session.")
        return

    # Authenticate the teacher by verifying biometric data
    print("Please scan your face to verify teacher identity.")
    biometric_data = None
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        biometric_data = capture_and_extract_encoding()
        if biometric_data is None:
            print(FAILED_CAPTURE_PROMPT)
            attempts += 1
            if attempts >= max_attempts:
                print("Failed to capture biometric data multiple times. Exiting session.")
                return
            continue
        break

    if biometric_data is None:
        print("Failed to capture biometric data. Exiting session.")
        return

    teacher_id = find_person_by_biometric(biometric_data, "teacher")
    if not teacher_id:
        print("Teacher verification failed. Cannot initiate the session.")
        return

    # Select the class for the session
    selected_class = select_class(teacher_id)
    if not selected_class:
        print("Error: No class selected. Cannot start the session.")
        return

    print(f"Teacher verified successfully. Starting the attendance session for {selected_class['subject_code']} - {selected_class['subject_name']}...")

    # Create the session
    session_id = create_attendance_session(selected_class)
    if not session_id:
        print("Error: Failed to create the attendance session.")
        return

    print("Session started successfully. Please begin scanning students for attendance.\n")
    
    marked_students = set()  # Track students already marked
    while True:
        biometric_data = capture_and_extract_encoding()
        if biometric_data is None:
            print(FAILED_CAPTURE_PROMPT)
            continue

        enrollment_id = find_person_by_biometric(biometric_data, "student")
        if enrollment_id:
            if enrollment_id not in marked_students: 
                # Use the updated record_attendance function
                record_attendance(session_id=session_id, 
                                  enrollment_id=enrollment_id, 
                                  biometric_data=biometric_data, 
                                  attendance_status="present")
                marked_students.add(enrollment_id)  # Add to marked list
                print(ATTENDANCE_SUCCESS.format("Student", enrollment_id))
            else:
                print(f"Attendance already marked for Student ID: {enrollment_id}")
        else:
            print("Student not found. Marking as absent.")
            absent_student_id = input("Enter Enrollment ID to mark absent (or press Enter to skip): ").strip()
            if absent_student_id:
                if absent_student_id.isdigit():
                    confirm = input(f"Are you sure you want to mark student {absent_student_id} as absent? (y/n): ").strip().lower()
                    if confirm == 'y':
                        record_attendance(session_id=session_id, 
                                          enrollment_id=int(absent_student_id), 
                                          biometric_data=None, 
                                          attendance_status="absent")
                        print(f"Attendance marked as absent for Enrollment ID: {absent_student_id}")
                    else:
                        print("Absent marking canceled.")
                else:
                    print("Invalid Enrollment ID. Skipping.")
            else:
                print("No attendance recorded for this student.")

        # Check if the teacher wants to end the session
        exit_choice = input(EXIT_PROMPT).lower()
        if exit_choice == 'exit':
            handle_close_session(session_id)
            print("Session successfully ended. All attendance has been recorded.")
            print(SESSION_END_PROMPT)
            break



def handle_close_session(session_id):
    print("General Info: To close a class session teacher need to scan its face\n")
    person_type = "teacher"
    print("Closing the attendance session...")
    # Verify teacher's biometric data
    biometric_data = capture_and_extract_encoding()  # No parameters passed

    if biometric_data is not None and biometric_data.size > 0:
        teacher_verified = find_person_by_biometric(biometric_data, person_type)
        if teacher_verified:
            close_attendance_session(session_id)  # Pass the session ID to close it
        else:
            print(TEACHER_VERIFICATION_FAIL)
    else:
        print("Failed to capture teacher biometric data.")




def close_attendance_session(session_id):
    """
    Close an ongoing attendance session.

    Args:
        session_id (int): The ID of the session to close.
    """
    db = get_db_connection()
    if db is None:
        logging.error("Database connection failed. Attendance session not closed.")
        return

    try:
        with db.cursor() as cursor:
            query = """UPDATE sessions SET status = 'completed', end_time = %s WHERE session_id = %s"""
            cursor.execute(query, (datetime.datetime.now(), session_id))
            db.commit()
            logging.info(f"Attendance session with ID {session_id} closed successfully.")
    except Exception as e:
        logging.error(f"Error while closing attendance session: {e}")
        db.rollback()




def create_attendance_session(selected_class):

    db = get_db_connection()
    if db is None:
        logging.error("Database connection failed. Cannot create attendance session.")
        return None

    try:
        with db.cursor() as cursor:
            query = """INSERT INTO sessions (available_class_id, teacher_id, start_time, status) 
                       VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (selected_class['available_class_id'], 
                                   selected_class['teacher_id'], 
                                   datetime.datetime.now(), 
                                   'ongoing'))
            db.commit()
            logging.info("Attendance session created successfully.")
            return cursor.lastrowid  # Get the ID of the newly created session

    except Exception as e:
        logging.error(f"Error while creating attendance session: {e}")
        db.rollback()
        return None


