import cv2
import csv
import os
from datetime import datetime
from utils import setup_folders, get_today, get_timestamp

setup_folders()

ATTENDANCE_FILE = "data/attendance.csv"

def already_marked(student_id):
    today = get_today()
    if not os.path.exists(ATTENDANCE_FILE):
        return False

    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == student_id and row[2] == today:
                return True
    return False

def mark_attendance(student_id, method):
    if already_marked(student_id):
        return False

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            student_id,
            method,
            get_today(),
            get_timestamp()
        ])
    return True

# OpenCV QR scanning
cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

print("QR Attendance started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data, bbox, _ = detector.detectAndDecode(frame)

    if data:
        success = mark_attendance(data, "QR")
        if success:
            print(f"[SUCCESS] Attendance marked for {data}")
        else:
            print(f"[INFO] Attendance already marked today for {data}")

    cv2.imshow("QR Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
