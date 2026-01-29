import cv2
import pickle
from utils import setup_folders, get_today, get_timestamp
import csv
import os

setup_folders()

ATTENDANCE_FILE = "data/attendance.csv"

face_cascade = cv2.CascadeClassifier(
    "src/haarcascade_frontalface_default.xml"
)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("models/face_model.yml")

with open("models/label_map.pkl", "rb") as f:
    label_map = pickle.load(f)

id_map = {v: k for k, v in label_map.items()}

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

def mark_attendance(student_id):
    if already_marked(student_id):
        return False

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            student_id,
            "FACE",
            get_today(),
            get_timestamp()
        ])
    return True

cap = cv2.VideoCapture(0)
print("Face attendance started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        roi = gray[y:y+h, x:x+w]
        label, confidence = recognizer.predict(roi)

        if confidence < 70 and label in id_map:
            student_id = id_map[label]
            success = mark_attendance(student_id)

            text = "Marked" if success else "Already Marked"
            cv2.putText(frame, f"{student_id} - {text}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Unknown",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 0, 255), 2)

        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    cv2.imshow("Face Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
