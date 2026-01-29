import cv2
import os

# Input student ID
STUDENT_ID = input("Enter student ID (8 digits): ").strip()
if not STUDENT_ID.isdigit() or len(STUDENT_ID) != 8:
    print("Invalid student ID. Must be 8 digits.")
    exit()

SAVE_DIR = f"smart_attendance/faces/{STUDENT_ID}"
os.makedirs(SAVE_DIR, exist_ok=True)

# Locate Haar cascade XML
face_cascade_path = os.path.join(os.path.dirname(__file__), "../haarcascade_frontalface_default.xml")
if not os.path.isfile(face_cascade_path):
    print("ERROR: Haar cascade XML not found. Download from OpenCV GitHub and place in project root.")
    exit()

face_cascade = cv2.CascadeClassifier(face_cascade_path)

cap = cv2.VideoCapture(0)
count = 0
print("Capturing faces. Press Q to stop or capture 30 images.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        face_img = gray[y:y+h, x:x+w]
        cv2.imwrite(f"{SAVE_DIR}/{count}.jpg", face_img)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("Face Registration", frame)

    if cv2.waitKey(1) & 0xFF == ord("q") or count >= 30:
        break

cap.release()
cv2.destroyAllWindows()
print("Face registration completed.")
