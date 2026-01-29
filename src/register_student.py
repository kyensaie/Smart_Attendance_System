import cv2
import csv
import os

# Paths relative to project root
FACES_DIR = "smart_attendance/data/faces"
STUDENTS_CSV = "smart_attendance/data/students.csv"

# this makes sure faces folder exists
os.makedirs(FACES_DIR, exist_ok=True)


def save_student_to_csv(student_id, name):
    file_exists = os.path.isfile(STUDENTS_CSV)

    with open(STUDENTS_CSV, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["student_id", "name"])

        writer.writerow([student_id, name])

    print("Student registered successfully.")


def register_student():
    student_id = input("Enter Student ID (8 digits): ").strip()
    name = input("Enter Full Name: ").strip()

    # Validate student ID
    if not student_id.isdigit() or len(student_id) != 8:
        print("Error: Student ID must be exactly 8 digits.")
        return

    # Validation for name (letters, spaces, hyphens only)
    clean_name = name.replace(" ", "").replace("-", "")
    if not clean_name.isalpha():
        print("Error: Name must contain only letters, spaces, or hyphens.")
        return

    # this opens webcam to take a photo
    cap = cv2.VideoCapture(0)
    print("Camera opened. Press 'S' to save face, 'Q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access camera.")
            break

        cv2.imshow("Register Student - Press S to Save", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            image_path = f"{FACES_DIR}/{student_id}.jpg"
            cv2.imwrite(image_path, frame)
            print("Face image saved.")

            save_student_to_csv(student_id, name)
            break

        elif key == ord('q'):
            print("Registration cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

#makes it run
if __name__ == "__main__":
    register_student()
