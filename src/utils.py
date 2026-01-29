import os
from src.utils import setup_folders

setup_folders()

while True:
    print("\nSMART ATTENDANCE SYSTEM")
    print("1. Register Student")
    print("2. Generate QR Codes")
    print("3. QR Attendance")
    print("4. Face Attendance")
    print("Q. Quit")

    choice = input("Select option: ").strip().upper()

    if choice == "1":
        os.system("python src/register_student.py")
    elif choice == "2":
        os.system("python src/generate_qr.py")
    elif choice == "3":
        os.system("python src/qr_attendance.py")
    elif choice == "4":
        os.system("python src/face_attendance.py")
    elif choice == "Q":
        print("Goodbye!")
        break
    else:
        print("Invalid choice.")
