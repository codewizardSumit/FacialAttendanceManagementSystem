
# ______________________________________________________________GETTING CURRENT MEAN ENCODING VIA THREADS_____________________________________________________________

import cv2
import os
import time
import shutil
import face_recognition
import numpy as np
import threading

def delete_directory(directory):
    """Deletes a directory and its contents."""
    try:
        shutil.rmtree(directory)
        print(f"Image directory '{directory}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting directory '{directory}': {e}")

def capture_images(cam, num_images, temp_image_dir, capture_event, encode_event, stop_event):
    """Thread function to capture images."""
    for i in range(num_images):
        if stop_event.is_set():  # Stop if the stop signal is set
            break

        capture_event.wait()  # Wait until the capture event is set
        capture_event.clear()

        ret, frame = cam.read()
        if not ret:
            print(f"Failed to grab frame {i + 1}. Skipping...")
            encode_event.set()  # Signal the encoding thread to proceed even if capture fails
            continue
        cv2.imshow("Capturing Image", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        temp_image_path = os.path.join(temp_image_dir, f"temp_face_{i + 1}.jpg")
        cv2.imwrite(temp_image_path, frame)
        print(f"Image {i + 1} captured.")

        encode_event.set()  # Signal the encoding thread to process this image
        time.sleep(1)  # Delay before capturing the next image

def process_encodings(temp_image_dir, num_images, encodings, capture_event, encode_event, stop_event):
    """Thread function to extract encodings."""
    for i in range(num_images):
        if stop_event.is_set():  # Stop if the stop signal is set
            break

        encode_event.wait()  # Wait until the encoding event is set
        encode_event.clear()

        temp_image_path = os.path.join(temp_image_dir, f"temp_face_{i + 1}.jpg")

        if not os.path.exists(temp_image_path):
            print(f"No image found for encoding {i + 1}, skipping...")
            capture_event.set()  # Signal the capture thread to proceed
            continue

        image = face_recognition.load_image_file(temp_image_path)
        face_encodings = face_recognition.face_encodings(image)

        if face_encodings:
            encodings.append(face_encodings[0])
            print(f"Captured encoding {i + 1}.")
        else:
            print(f"No face found in image {i + 1}, skipping...")

        os.remove(temp_image_path)  # Clean up the processed image
        capture_event.set()  # Signal the capture thread to proceed
        time.sleep(1)

def capture_and_extract_encoding(num_images=5, temp_image_dir="temp_images"):
    """Main function to handle image capturing and encoding extraction."""
    if not os.path.exists(temp_image_dir):
        os.makedirs(temp_image_dir)

    encodings = []
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Error: Camera could not be opened.")
        return None

    print(f"Capturing {num_images} images...")

    # Events for thread synchronization
    capture_event = threading.Event()
    encode_event = threading.Event()
    stop_event = threading.Event()

    # Threads for capturing images and processing encodings
    capture_thread = threading.Thread(target=capture_images, args=(cam, num_images, temp_image_dir, capture_event, encode_event, stop_event))
    encoding_thread = threading.Thread(target=process_encodings, args=(temp_image_dir, num_images, encodings, capture_event, encode_event, stop_event))

    capture_thread.start()
    encoding_thread.start()

    capture_event.set()  # Start the capture process

    # Wait for both threads to finish
    capture_thread.join()
    encoding_thread.join()

    # Cleanup resources
    cam.release()
    cv2.destroyAllWindows()

    if not encodings:
        print("No valid encodings captured.")
        delete_directory(temp_image_dir)
        return None

    # Calculate the mean encoding
    mean_encoding = np.mean(encodings, axis=0)
    print("Mean encoding calculated.")

    # Delete the temporary image directory
    delete_directory(temp_image_dir)

    return mean_encoding