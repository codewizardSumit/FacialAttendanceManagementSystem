# Attendance Management System (AMS)

## **Overview**
The Attendance Management System (AMS) is a Python-based project that leverages biometric data (face recognition) to simplify attendance tracking for teachers and students. Using facial recognition technology, the system can register users, capture face data, and record attendance seamlessly.

## **Features**
1. **Biometric Registration**:
   - Register teachers and students by capturing their facial data.
   - Save biometric data securely in a MySQL database.

2. **Attendance Tracking**:
   - Recognize faces in real time using a live camera feed.
   - Mark attendance automatically based on facial recognition.

3. **Database Integration**:
   - Store user details and biometric encodings in a MySQL database.
   - Maintain logs of attendance sessions.

4. **Fallback Mechanism**:
   - Backup method for face data registration using pre-captured images in case live capturing fails.

## **Technologies Used**
- **Programming Language**: Python
- **Database**: MySQL
- **Libraries**:
  - `face-recognition`: Facial recognition functionality.
  - `opencv-python`: Real-time video and image processing.
  - `numpy`: Array manipulation for image processing.
  - `mysql-connector-python`: MySQL database connectivity.

## **Setup Instructions**

### **Prerequisites**
1. Install Python (>= 3.8).
2. Set up a MySQL database and create a database named `ams`.
3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

### **Steps**
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Configure the database:
   - Update `DBconfig.py` with your MySQL credentials.

3. Run the application:
   ```bash
   python main.py
   ```

## **Project Structure**
```
AMS/
├── DBconfig.py                 # Database connection configuration
├── README.md                   # Project documentation
├── attendances.py              # Manages attendance sessions
├── biometric_utils.py          # Utility functions for biometric data handling
├── classUtils.py               # Class and session utilities
├── getCurrentEncodings.py      # Fetch current face encodings
├── getMeanEncodings.py         # Calculate mean face encodings
├── haarcascade_frontalface_default.xml  # Haar Cascade model for face detection
├── main.py                     # Entry point for the application
├── register.py                 # Handles user registration (teacher/student)
├── requirements.txt            # Required Python packages
├── session_utils.py            # Utility functions for session handling
|-- ams_schema.sql              # AMS database schema file

```

## **Usage**
1. **Register Users**:
   - Run the `register.py` script to register teachers and students.
2. **Capture Face Data**:
   - Use `faceDetect.py` to capture biometric data for users.
3. **Mark Attendance**:
   - Start an attendance session using `attendance.py`.

## **Contributing**
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes and open a pull request.

## **License**
This project is licensed under the [MIT License](LICENSE).

## **Acknowledgments**
- Special thanks to the open-source community for providing tools and libraries used in this project.
- Inspired by the need for efficient and automated attendance systems in educational institutions.
- Obviously created the project with the help of AI tools (ChatGPT and Gemini).

---
For further assistance, feel free to contact us at ethicalweb01@gmail.com

