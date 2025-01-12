import mysql.connector
import logging
from DBconfig import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='class_utils.log')

def get_distinct_subjects():
    """
    Fetch distinct subjects from the database.
    """
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if db is None:
            logging.error("Failed to connect to the database.")
            return []

        cursor = db.cursor(dictionary=True)

        query = """
            SELECT DISTINCT s.subject_id, s.subject_code, s.subject_name
            FROM availableclasses ac
            JOIN subjects s ON ac.subject_id = s.subject_id;
        """
        cursor.execute(query)

        subjects = cursor.fetchall()
        return subjects
    except mysql.connector.Error as err:
        logging.error(f"Database error in get_distinct_subjects(): {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def get_sections_for_subject(subject_id):
    """
    Fetch sections for a given subject ID.
    """
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if db is None:
            logging.error("Failed to connect to the database.")
            return []

        cursor = db.cursor(dictionary=True)

        query = """
            SELECT ac.available_class_id, sec.section
            FROM availableclasses ac
            JOIN sections sec ON ac.section_id = sec.section_id
            WHERE ac.subject_id = %s;
        """
        cursor.execute(query, (subject_id,))

        sections = cursor.fetchall()
        return sections
    except mysql.connector.Error as err:
        logging.error(f"Database error in get_sections_for_subject(): {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
def select_class(teacher_id):
    """
    Display a list of subjects, allow the teacher to select one, 
    and then choose the corresponding section.
    Also, include teacher_id in the returned class dictionary.
    """
    subjects = get_distinct_subjects()

    if not subjects:
        print("No available subjects found.")
        return None

    print("\n===== Select Subject =====")
    for index, subject in enumerate(subjects):
        display_string = f"{index + 1}. {subject['subject_code']} - {subject['subject_name']}"
        print(display_string)

    while True:  # Subject selection loop
        subject_choice = input("Select the subject number: ")
        try:
            subject_index = int(subject_choice) - 1
            if 0 <= subject_index < len(subjects):
                selected_subject = subjects[subject_index]
                break
            else:
                print("Invalid subject selection. Please enter a number within the displayed range.")
                logging.warning(f"Invalid subject selection input: {subject_choice}")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            logging.warning(f"Invalid input type for subject selection: {subject_choice}")

    sections = get_sections_for_subject(selected_subject['subject_id'])

    if not sections:
        print("No sections available for the selected subject.")
        return None

    print("\n===== Select Section =====")
    for index, section in enumerate(sections):
        display_string = f"{index + 1}. Section: {section['section']}"
        print(display_string)

    while True:  # Section selection loop
        section_choice = input("Select the section number: ")
        try:
            section_index = int(section_choice) - 1
            if 0 <= section_index < len(sections):
                selected_section = sections[section_index]
                selected_class = {
                    **selected_subject,
                    **selected_section,
                    "teacher_id": teacher_id  # Add the teacher's ID to the class dictionary
                }
                return selected_class
            else:
                print("Invalid section selection. Please enter a number within the displayed range.")
                logging.warning(f"Invalid section selection input: {section_choice}")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            logging.warning(f"Invalid input type for section selection: {section_choice}")

