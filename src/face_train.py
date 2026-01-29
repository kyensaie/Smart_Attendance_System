import cv2
import os
import numpy as np
import pickle

DATASET_DIR = "smart_attendance/faces"
MODEL_DIR = "smart_attendance/models"
MODEL_PATH = f"{MODEL_DIR}/face_model.yml"
LABEL_MAP_PATH = f"{MODEL_DIR}/label_map.pkl"

os.makedirs(MODEL_DIR, exist_ok=True)

faces = []
labels = []
label_map = {}
current_label = 0

for student_id in os.listdir(DATASET_DIR):
    student_path = os.path.join(DATASET_DIR, student_id)
    if not os.path.isdir(student_path):
        continue

    label_map[current_label] = student_id

    for img_name in os.listdir(student_path):
        img_path = os.path.join(student_path, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            faces.append(img)
            labels.append(current_label)

    current_label += 1

if not faces:
    print("ERROR: No faces found. Register students first.")
    exit()

# Create LBPH recognizer
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
except AttributeError:
    print("ERROR: cv2.face module not found. Install opencv-contrib-python.")
    exit()

recognizer.train(faces, np.array(labels))
recognizer.save(MODEL_PATH)

# Save label map for attendance lookup
with open(LABEL_MAP_PATH, "wb") as f:
    pickle.dump(label_map, f)

print("Face model trained successfully.")
