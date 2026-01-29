# Smart Attendance System

## Overview

The **Smart Attendance System** is a Python-based application designed to automate student attendance recording using **QR Code technology** and or **Face Recognition**. The system is suitable especially  for academic environments and provides both a command-line interface (CLI) and a graphical user interface (GUI).

The application supports student registration with extended information such as **email address** and **course of study**, generates unique QR codes, and records attendance accurately while minimizing impersonation and manual errors.


## Features

* Student registration with name, index number, email, and course of study
* Face image capture and face model training using OpenCV
* Persistent face recognition model for reuse across sessions
* QR code generation for individual students
* Attendance recording using either QR codes or face recognition
* Attendance records stored in CSV format
* Menu-driven CLI and optional GUI implementation


## Project Structure

smart_attendance/
│
├── data/                     # Student records and attendance logs
├── faces/                    # Captured face images for training
├── models/                   # Trained face recognition model and label map
│   ├── face_model.yml
│   └── label_map.pkl
│
├── src/
│   ├── main.py               # Main application menu
│   ├── register_student.py   # Student registration module
│   ├── generate_qr.py        # QR code generation module
│   ├── qr_attendance.py      # QR-based attendance module
│   ├── face_register.py      # Face image capture module
│   ├── face_train.py         # Face recognition model training
│   ├── face_attendance.py    # Face-based attendance module
│   ├── utils.py              # Utility/helper functions
│   └── haarcascade_frontalface_default.xml
│
├── gui_main.py               # Graphical user interface implementation
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation


## Requirements

The project requires **Python 3.8 or higher**.

Install all dependencies using:

```bash
pip install -r requirements.txt
```

### requirements.txt

```
opencv-contrib-python
numpy
qrcode
pillow
```

---

## Running the Application

### Command-Line Interface (CLI)

From the project root directory:

```bash
python src/main.py
```

The CLI provides the following options:

```
1. Register Student
2. Generate QR Codes
3. QR Attendance
4. Face Attendance
Q. Quit
```

---

### Graphical User Interface (GUI)

To run the GUI version:

```bash
python gui_main.py
```

The GUI allows users to:

* Register students
* Generate QR codes
* Record attendance using QR codes
* Record attendance using face recognition

---

## System Workflow

1. **Student Registration**
   Students are registered with personal and academic details, including email and course of study.

2. **Face Capture and Training**
   Face images are captured and used to train the face recognition model.

3. **QR Code Generation**
   A unique QR code is generated for each registered student.

4. **Attendance Recording**
   Attendance can be recorded using either QR code scanning or face recognition.

All attendance data is stored automatically for future reference.

---

## Error Handling

* Detects and reports missing face models
* Prevents duplicate attendance entries
* Handles invalid inputs and unknown faces or QR codes

---

## Limitations

- Face recognition accuracy depends on lighting conditions and camera quality.
- The system does not currently support cloud storage or remote databases.
- Attendance is limited to one record per student per day.
- The system is designed for small to medium class sizes.
- No user authentication is implemented for administrative access.

These limitations can be addressed in future versions.


## Future Enhancements

* Database integration (e.g., SQLite or MySQL)
* Cloud-based data storage
* User authentication and role management
* Enhanced GUI design
* Export of attendance records to Excel

---

## Author

**Kwaku Yeboah Antwi**
Class of 2028

---

## License

This project is intended for **educational purposes** only.


