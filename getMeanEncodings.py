
#_____________________________________ MEAN ENCODING CAPTURING VIA THREADS _____________________________________
import cv2
import os
import face_recognition
import numpy as np
import time
import shutil
from threading import Thread, Lock

def capture_and_extract_mean_encoding(num_images=10, save_dir='temp_images', instructions=None, frame_size=(640, 480)):
    """
    Captures images with user instructions, extracts mean face encodings, and cleans up the directory.
    
    Returns:
        mean_encoding (numpy array): The calculated mean encoding of the captured faces.
    """

    def save_image(image, filename):
        """Save an image synchronously."""
        cv2.imwrite(filename, image)

    def delete_directory(directory):
        """Deletes a directory and its contents."""
        try:
            shutil.rmtree(directory)
            print(f"Image directory '{directory}' deleted successfully.")
        except Exception as e:
            print(f"Error deleting directory '{directory}': {e}")

    def capture_images(cam, save_dir, instructions, num_images, captured_images, lock):
        """Capture images based on the instructions."""
        for idx, instruction in enumerate(instructions):
            if captured_images >= num_images:
                break

            print(f"Instruction: {instruction}")
            print("Position yourself as instructed.")

            # Countdown before capture
            for countdown in range(1, 0, -1):
                print(f"Capturing in {countdown}...")
                time.sleep(1)

            for _ in range(num_images // len(instructions)):  # Distribute images across instructions
                ret, frame = cam.read()
                if not ret:
                    print("Failed to grab frame. Retrying...")
                    continue

                # Show the current frame with instruction
                cv2.putText(frame, f"Instruction: {instruction}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow("Capturing Face", frame)
                cv2.waitKey(1)  # Allow OpenCV to update the window

                # Save the image synchronously
                image_filename = os.path.join(save_dir, f"{instruction.replace(' ', '_')}_{captured_images + 1}.jpg")
                with lock:
                    save_image(frame, image_filename)
                    captured_images += 1

                print(f"Captured {captured_images}/{num_images} images.")

                if captured_images >= num_images:
                    break

                time.sleep(1)  # Pause briefly for the user to reposition

    def encode_faces(save_dir, lock, encodings_list):
        """Extract face encodings from the saved images."""
        for image_filename in os.listdir(save_dir):
            image_path = os.path.join(save_dir, image_filename)
            image = face_recognition.load_image_file(image_path)

            # Find face encodings
            face_encodings = face_recognition.face_encodings(image)
            if len(face_encodings) > 0:
                with lock:
                    encodings_list.append(face_encodings[0])
            else:
                print(f"No face detected in {image_filename}, skipping...")

    # Initialize camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Camera could not be opened.")
        return None

    # Set frame size
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])

    # Ensure save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    captured_images = 0
    instructions = instructions or ["Center", "Tilt Left", "Tilt Right", "Tilt Up", "Tilt Down"]

    print(f"Capturing {num_images} images at resolution {frame_size[0]}x{frame_size[1]}...")

    # Lock for synchronizing access to shared resources
    lock = Lock()

    # Threads to capture images and encode faces
    encodings_list = []
    capture_thread = Thread(target=capture_images, args=(cam, save_dir, instructions, num_images, captured_images, lock))
    encoding_thread = Thread(target=encode_faces, args=(save_dir, lock, encodings_list))

    # Start the capture thread
    capture_thread.start()

    # Wait for capture thread to finish before starting encoding
    capture_thread.join()

    # Start encoding thread
    encoding_thread.start()

    # Wait for encoding thread to finish
    encoding_thread.join()

    # Release the camera and close the window
    cam.release()
    cv2.destroyAllWindows()

    # Check if any face encodings were captured
    if not encodings_list:
        print("No face encodings were captured.")
        delete_directory(save_dir)
        return None

    # Calculate mean encoding
    mean_encoding = np.mean(encodings_list, axis=0)
    #np.save("mean_encoding.npy", mean_encoding)
    print("Mean encoding calculated and saved.")

    # Clean up saved images
    delete_directory(save_dir)

    return mean_encoding


