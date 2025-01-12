import logging
from session_utils import handle_attendance_session
# Initialize logging
logging.basicConfig(level=logging.INFO)

def main_menu():
    """
    Display the main menu and handle user input.
    """
    while True:
        print("\n===== Main Menu =====")
        print("1. Start Attendance")
        print("2. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            handle_attendance_session()
        elif choice == '2':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")



if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
