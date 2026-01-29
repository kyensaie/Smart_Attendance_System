import qrcode
import os
import csv

# Paths
QR_DIR = "smart_attendance/src/qr_codes"
STUDENTS_CSV = "smart_attendance/data/students.csv"

# Make sure QR folder exists
os.makedirs(QR_DIR, exist_ok=True)

# Generate QR for one student
def generate_qr_for_student(student_id):
    student_id = student_id.strip()

    # Validate student ID
    if not student_id.isdigit() or len(student_id) != 8:
        print(f"Error: Student ID '{student_id}' must be exactly 8 digits.")
        return False

    img_path = f"{QR_DIR}/{student_id}.png"
    if os.path.isfile(img_path):
        print(f"QR for {student_id} already exists at {img_path}.")
        return "exists"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(student_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(img_path)
    print(f"QR code saved for {student_id} at {img_path}")
    return True


# Generate QR for all students
def generate_qr_for_all():
    if not os.path.isfile(STUDENTS_CSV):
        print("No students found. Register students first.")
        return

    with open(STUDENTS_CSV, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            student_id = row.get("student_id", "").strip()
            if not student_id:
                continue  # skip empty rows

            while True:
                result = generate_qr_for_student(student_id)
                if result == True:
                    break  # QR created successfully
                elif result == "exists":
                    # Ask user what to do
                    choice = input(f"QR for {student_id} exists. Skip (S) or enter new ID (N)? ").strip().upper()
                    if choice == "S":
                        print(f"Skipping {student_id}.")
                        break
                    elif choice == "N":
                        student_id = input("Enter new 8-digit Student ID: ").strip()
                    else:
                        print("Invalid choice. Type S to skip or N to enter new ID.")
                else:
                    # Invalid student ID
                    choice = input(f"Invalid student ID '{student_id}'. Skip (S) or enter new ID (N)? ").strip().upper()
                    if choice == "S":
                        print(f"Skipping {student_id}.")
                        break
                    elif choice == "N":
                        student_id = input("Enter new 8-digit Student ID: ").strip()
                    else:
                        print("Invalid choice. Type S to skip or N to enter new ID.")


if __name__ == "__main__":
    while True:
        print("\n1. Generate QR for one student")
        print("2. Generate QR for all students")
        print("Q. Quit")
        choice = input("Enter choice (1, 2, or Q): ").strip().upper()

        if choice == "1":
            while True:
                student_id = input("Enter Student ID (8 digits): ").strip()
                result = generate_qr_for_student(student_id)
                if result == True:
                    break
                elif result == "exists":
                    sub_choice = input(f"QR for {student_id} exists. Skip (S) or enter new ID (N)? ").strip().upper()
                    if sub_choice == "S":
                        break
                    elif sub_choice == "N":
                        continue
                    else:
                        print("Invalid choice. Type S to skip or N to enter new ID.")
                else:
                    sub_choice = input(f"Invalid student ID '{student_id}'. Skip (S) or enter new ID (N)? ").strip().upper()
                    if sub_choice == "S":
                        break
                    elif sub_choice == "N":
                        continue
                    else:
                        print("Invalid choice. Type S to skip or N to enter new ID.")

        elif choice == "2":
            generate_qr_for_all()

        elif choice == "Q":
            print("Exiting QR generator.")
            break

        else:
            print("Error: Invalid choice. Enter 1, 2, or Q only.")
