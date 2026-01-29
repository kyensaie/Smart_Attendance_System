import tkinter as tk
from tkinter import messagebox, ttk
import os
import csv
import cv2
import qrcode
import pickle
from datetime import datetime
import threading

#  Paths 
STUDENTS_CSV = "smart_attendance/data/students.csv"
ATTENDANCE_CSV = "smart_attendance/data/attendance.csv"
QR_DIR = "smart_attendance/qr_codes"  # Changed to be more visible
FACE_MODEL_PATH = "smart_attendance/models/face_model.yml"
LABEL_MAP_PATH = "smart_attendance/models/label_map.pkl"
FACE_DIR = "smart_attendance/faces"
# This tries multiple possible locations for Haar cascade especially if not found
HAAR_PATH = None
possible_haar_paths = [
    "haarcascade_frontalface_default.xml",
    "smart_attendance/haarcascade_frontalface_default.xml",
    os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml"),
    "/mnt/user-data/uploads/haarcascade_frontalface_default.xml"
]

for path in possible_haar_paths:
    if os.path.isfile(path):
        HAAR_PATH = path
        break

# Create necessary directories
os.makedirs(QR_DIR, exist_ok=True)
os.makedirs(os.path.dirname(ATTENDANCE_CSV), exist_ok=True)
os.makedirs(os.path.dirname(FACE_MODEL_PATH), exist_ok=True)
os.makedirs(FACE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(STUDENTS_CSV), exist_ok=True)

#  Color Scheme 
BG_COLOR = "#FFFFFF"  # White
TEXT_COLOR = "#000000"  # Black
ACCENT_COLOR = "#2196F3"  # Blue
BUTTON_BG = "#2196F3"  # Blue
BUTTON_FG = "#FFFFFF"  # White
BUTTON_HOVER = "#1976D2"  # Darker Blue

# Helper Functions

def load_students():
    if not os.path.isfile(STUDENTS_CSV):
        return {}
    students = {}
    try:
        with open(STUDENTS_CSV, newline="", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Check if required columns exist
            if reader.fieldnames is None or 'student_id' not in reader.fieldnames or 'name' not in reader.fieldnames:
                print("ERROR: students.csv is missing required columns (student_id, name)")
                print(f"Found columns: {reader.fieldnames}")
                return {}
            
            for row in reader:
                if row.get("student_id") and row.get("name"):
                    students[row["student_id"].strip()] = {
                        'name': row["name"].strip(),
                        'course': row.get("course", "").strip(),
                        'email': row.get("email", "").strip()
                    }
    except Exception as e:
        print(f"ERROR loading students.csv: {e}")
        return {}
    return students

def mark_attendance(student_id, student_data):
    if not os.path.isfile(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id","name","course","email","date","time"])
    now = datetime.now()
    name = student_data['name'] if isinstance(student_data, dict) else student_data
    course = student_data.get('course', '') if isinstance(student_data, dict) else ''
    email = student_data.get('email', '') if isinstance(student_data, dict) else ''
    
    with open(ATTENDANCE_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([student_id, name, course, email, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])

# this shows the GUI Application

class SmartAttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance System")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)
        
        self.camera_active = False
        
        # Check and fix students.csv if needed
        self.check_students_csv()
        
        # Header
        header = tk.Label(
            root, 
            text="SMART ATTENDANCE SYSTEM", 
            font=("Arial", 24, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        )
        header.pack(pady=30)
        
        # Button Frame
        button_frame = tk.Frame(root, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        # Buttons
        self.create_button(button_frame, "Register Student", self.register_student, 0)
        self.create_button(button_frame, "Generate QR Codes", self.generate_qr, 1)
        self.create_button(button_frame, "QR Attendance", self.qr_attendance, 2)
        self.create_button(button_frame, "Face Attendance", self.face_attendance, 3)
        self.create_button(button_frame, "View Attendance Records", self.view_attendance, 4)
        self.create_button(button_frame, "Exit", self.exit_app, 5)
        
        # Status Label
        self.status_label = tk.Label(
            root,
            text="Ready",
            font=("Arial", 12),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.status_label.pack(pady=20)
        
    def create_button(self, parent, text, command, row):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 14),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            width=20,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn.grid(row=row, column=0, pady=10, padx=20)
        
        # Hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_BG))
        
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
    
    def check_students_csv(self):
        """Check if students.csv exists and has correct format"""
        if not os.path.isfile(STUDENTS_CSV):
            # Create new file with headers
            os.makedirs(os.path.dirname(STUDENTS_CSV), exist_ok=True)
            with open(STUDENTS_CSV, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["student_id", "name", "course", "email"])
            return
        
        # Check if file has correct headers
        try:
            with open(STUDENTS_CSV, "r", newline="", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                required_columns = ['student_id', 'name', 'course', 'email']
                missing_columns = [col for col in required_columns if col not in (reader.fieldnames or [])]
                
                if missing_columns:
                    # Fix the file
                    response = messagebox.askyesno(
                        "CSV Format Error",
                        f"students.csv is missing columns: {', '.join(missing_columns)}\n" +
                        f"Current columns: {reader.fieldnames}\n\n" +
                        "Do you want to recreate it with correct format?\n" +
                        "(This will delete existing data)"
                    )
                    if response:
                        with open(STUDENTS_CSV, "w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(["student_id", "name", "course", "email"])
                        messagebox.showinfo("Success", "students.csv has been recreated with correct format")
        except Exception as e:
            messagebox.showerror("Error", f"Error checking students.csv: {str(e)}")
        
    def register_student(self):
        if self.camera_active:
            messagebox.showwarning("Warning", "Camera is already in use!")
            return
            
        register_window = tk.Toplevel(self.root)
        register_window.title("Register Student")
        register_window.geometry("500x450")
        register_window.configure(bg=BG_COLOR)
        
        # Title
        tk.Label(
            register_window, 
            text="Student Registration", 
            font=("Arial", 16, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        ).pack(pady=15)
        
        # Student ID
        tk.Label(register_window, text="Student ID (8 digits):", font=("Arial", 11), bg=BG_COLOR).pack(pady=(10,0))
        id_entry = tk.Entry(register_window, font=("Arial", 11), width=35)
        id_entry.pack(pady=5)
        
        # Student Name
        tk.Label(register_window, text="Full Name:", font=("Arial", 11), bg=BG_COLOR).pack(pady=(10,0))
        name_entry = tk.Entry(register_window, font=("Arial", 11), width=35)
        name_entry.pack(pady=5)
        
        # Course of Study
        tk.Label(register_window, text="Course of Study:", font=("Arial", 11), bg=BG_COLOR).pack(pady=(10,0))
        course_entry = tk.Entry(register_window, font=("Arial", 11), width=35)
        course_entry.pack(pady=5)
        
        # School Email
        tk.Label(register_window, text="School Email:", font=("Arial", 11), bg=BG_COLOR).pack(pady=(10,0))
        email_entry = tk.Entry(register_window, font=("Arial", 11), width=35)
        email_entry.pack(pady=5)
        
        # Validation messages label
        validation_label = tk.Label(
            register_window, 
            text="", 
            font=("Arial", 9), 
            bg=BG_COLOR, 
            fg="red",
            wraplength=400
        )
        validation_label.pack(pady=5)
        
        def validate_email(email):
            """Validate school email format"""
            import re
            # Basic email pattern
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        
        def save_student():
            student_id = id_entry.get().strip()
            name = name_entry.get().strip()
            course = course_entry.get().strip()
            email = email_entry.get().strip()
            
            # Clear previous validation messages
            validation_label.config(text="")
            
            # Validate Student ID
            if not student_id:
                validation_label.config(text="❌ Student ID cannot be empty!")
                id_entry.focus()
                return
            if not student_id.isdigit():
                validation_label.config(text="❌ Student ID must contain only numbers!")
                id_entry.focus()
                return
            if len(student_id) != 8:
                validation_label.config(text="❌ Student ID must be exactly 8 digits!")
                id_entry.focus()
                return
            
            # Check if student ID already exists
            existing_students = load_students()
            if student_id in existing_students:
                validation_label.config(text="❌ Student ID already registered!")
                id_entry.focus()
                return
            
            # Validate Name
            if not name:
                validation_label.config(text="❌ Name cannot be empty!")
                name_entry.focus()
                return
            if len(name) < 2:
                validation_label.config(text="❌ Name is too short!")
                name_entry.focus()
                return
            # Only letters, spaces, and hyphens allowed
            clean_name = name.replace(" ", "").replace("-", "")
            if not clean_name.isalpha():
                validation_label.config(text="❌ Name can only contain letters, spaces, and hyphens!")
                name_entry.focus()
                return
            
            # Validate Course
            if not course:
                validation_label.config(text="❌ Course of Study cannot be empty!")
                course_entry.focus()
                return
            if len(course) < 2:
                validation_label.config(text="❌ Course name is too short!")
                course_entry.focus()
                return
            # Allow letters, numbers, spaces, hyphens, and ampersand for courses
            allowed_course_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -&()")
            if not all(c in allowed_course_chars for c in course):
                validation_label.config(text="❌ Course contains invalid characters!")
                course_entry.focus()
                return
            
            # Validate Email
            if not email:
                validation_label.config(text="❌ School Email cannot be empty!")
                email_entry.focus()
                return
            if not validate_email(email):
                validation_label.config(text="❌ Invalid email format! (e.g., student@school.edu)")
                email_entry.focus()
                return
            
            # Save to CSV
            try:
                file_exists = os.path.isfile(STUDENTS_CSV)
                os.makedirs(os.path.dirname(STUDENTS_CSV), exist_ok=True)
                
                with open(STUDENTS_CSV, mode="a", newline="", encoding='utf-8') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["student_id", "name", "course", "email"])
                    writer.writerow([student_id, name, course, email])
                
                messagebox.showinfo("Success", 
                    f"✓ Student Registered Successfully!\n\n" +
                    f"ID: {student_id}\n" +
                    f"Name: {name}\n" +
                    f"Course: {course}\n" +
                    f"Email: {email}"
                )
                register_window.destroy()
                self.update_status(f"Registered: {name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save student:\n{str(e)}")
        
        # Buttons frame
        btn_frame = tk.Frame(register_window, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Register",
            command=save_student,
            font=("Arial", 12),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            width=12,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=register_window.destroy,
            font=("Arial", 12),
            bg="#757575",
            fg=BUTTON_FG,
            width=12,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
    def generate_qr(self):
        students = load_students()
        if not students:
            messagebox.showerror("Error", 
                "No students found!\n\n" +
                "Possible issues:\n" +
                "1. No students registered yet\n" +
                "2. students.csv is missing or corrupted\n" +
                "3. students.csv doesn't have correct columns (student_id, name, course, email)\n\n" +
                f"Expected file location: {STUDENTS_CSV}"
            )
            return
        
        try:
            # Make sure QR directory exists
            os.makedirs(QR_DIR, exist_ok=True)
            
            count = 0
            for student_id in students.keys():
                img_path = os.path.join(QR_DIR, f"{student_id}.png")
                if os.path.isfile(img_path):
                    continue
                
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
                count += 1
            
            # Get absolute path for display
            abs_qr_path = os.path.abspath(QR_DIR)
            
            if count == 0:
                result = messagebox.askquestion(
                    "QR Codes Already Exist",
                    f"All {len(students)} students already have QR codes!\n\n" +
                    f"Location: {abs_qr_path}\n\n" +
                    "Do you want to open the folder?"
                )
                if result == 'yes':
                    self.open_folder(abs_qr_path)
            else:
                result = messagebox.askquestion(
                    "QR Codes Generated!",
                    f"✓ Successfully generated {count} new QR codes!\n\n" +
                    f"Total students: {len(students)}\n" +
                    f"QR codes saved in:\n{abs_qr_path}\n\n" +
                    "Do you want to open the folder?"
                )
                if result == 'yes':
                    self.open_folder(abs_qr_path)
            
            self.update_status(f"Generated {count} QR codes in {QR_DIR}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR codes:\n{str(e)}")
            self.update_status("QR generation failed")
    
    def open_folder(self, path):
        """Open folder in file explorer"""
        try:
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
        
    def qr_attendance(self):
        if self.camera_active:
            messagebox.showwarning("Warning", "Camera is already in use!")
            return
            
        students = load_students()
        if not students:
            messagebox.showwarning("Warning", "No students registered!")
            return
        
        # Show instructions
        instructions = messagebox.askokcancel(
            "QR Attendance Instructions",
            "📱 HOW TO SCAN QR CODES:\n\n" +
            "1. Generated QR codes are in: smart_attendance/qr_codes/\n" +
            "2. Students should display their QR code (print or on phone screen)\n" +
            "3. Hold the QR code in front of the camera\n" +
            "4. Wait for the beep/confirmation\n" +
            "5. Press 'Q' on the camera window to stop\n\n" +
            "Ready to start?"
        )
        
        if not instructions:
            return
        
        self.camera_active = True
        self.update_status("QR Attendance Active - Show QR codes to camera")
        
        def run_qr_attendance():
            try:
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    messagebox.showerror("Error", "Cannot access camera!")
                    self.camera_active = False
                    self.update_status("Camera access failed")
                    return
                
                marked = set()
                detector = cv2.QRCodeDetector()
                
                # Add text overlay helper
                def add_text_overlay(frame, text, position=(10, 30), color=(0, 255, 0)):
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, text, position, font, 0.7, color, 2)
                
                print("\n" + "="*50)
                print("QR ATTENDANCE STARTED")
                print("Show QR codes to the camera")
                print("Press 'Q' to stop")
                print("="*50 + "\n")
                
                while self.camera_active:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Add instruction overlay
                    add_text_overlay(frame, "Show QR Code Here", (10, 30), (255, 255, 255))
                    add_text_overlay(frame, f"Marked: {len(marked)}", (10, 60), (0, 255, 0))
                    
                    data, bbox, _ = detector.detectAndDecode(frame)
                    
                    if data:
                        student_id = data.strip()
                        
                        # Draw bounding box if QR detected
                        if bbox is not None:
                            bbox = bbox.astype(int)
                            cv2.polylines(frame, [bbox], True, (0, 255, 0), 3)
                        
                        if student_id in students:
                            if student_id not in marked:
                                student_info = students[student_id]
                                mark_attendance(student_id, student_info)
                                marked.add(student_id)
                                
                                name = student_info['name']
                                print(f"✓ MARKED: {student_id} - {name}")
                                
                                # Visual feedback
                                add_text_overlay(frame, f"MARKED: {name}", (10, 100), (0, 255, 0))
                            else:
                                add_text_overlay(frame, "Already Marked!", (10, 100), (0, 255, 255))
                        else:
                            add_text_overlay(frame, "Unknown Student!", (10, 100), (0, 0, 255))
                            print(f"✗ UNKNOWN ID: {student_id}")
                    
                    cv2.imshow("QR Attendance - Press Q to Quit", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                
                print("\n" + "="*50)
                print(f"QR ATTENDANCE ENDED - Total Marked: {len(marked)}")
                print("="*50 + "\n")
                
                messagebox.showinfo("Attendance Complete", 
                    f"QR Attendance session ended.\n\n" +
                    f"Total students marked: {len(marked)}"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"QR Attendance failed:\n{str(e)}")
            finally:
                self.camera_active = False
                self.update_status("QR Attendance Stopped")
        
        thread = threading.Thread(target=run_qr_attendance)
        thread.daemon = True
        thread.start()
        
    def face_attendance(self):
        if self.camera_active:
            messagebox.showwarning("Warning", "Camera is already in use!")
            return
        
        # Check if Haar cascade file exists
        if HAAR_PATH is None or not os.path.isfile(HAAR_PATH):
            messagebox.showerror("Error", 
                "Haar cascade file not found!\n\n" +
                "Please ensure 'haarcascade_frontalface_default.xml' is in:\n" +
                "- Project root directory, OR\n" +
                "- smart_attendance/ directory, OR\n" +
                "- Same directory as this script"
            )
            return
            
        if not os.path.isfile(FACE_MODEL_PATH) or not os.path.isfile(LABEL_MAP_PATH):
            messagebox.showerror("Error", 
                "Face model not found!\n\n" +
                "Please run face training first:\n" +
                "1. Register student faces\n" +
                "2. Run face_train.py to create the model"
            )
            return
        
        students = load_students()
        if not students:
            messagebox.showwarning("Warning", "No students registered!")
            return
        
        self.camera_active = True
        self.update_status("Face Attendance Active - Press Q to stop")
        
        def run_face_attendance():
            try:
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.read(FACE_MODEL_PATH)
                
                with open(LABEL_MAP_PATH, "rb") as f:
                    label_map = pickle.load(f)
                
                face_cascade = cv2.CascadeClassifier(HAAR_PATH)
                
                if face_cascade.empty():
                    messagebox.showerror("Error", f"Failed to load Haar cascade from: {HAAR_PATH}")
                    self.camera_active = False
                    self.update_status("Haar cascade load failed")
                    return
                
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    messagebox.showerror("Error", "Cannot access camera!")
                    self.camera_active = False
                    self.update_status("Camera access failed")
                    return
                
                marked = set()
                
                while self.camera_active:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        face_img = gray[y:y+h, x:x+w]
                        label, confidence = recognizer.predict(face_img)
                        
                        if confidence < 70:
                            student_id = label_map.get(label, None)
                            if student_id and student_id in students:
                                if student_id not in marked:
                                    student_info = students[student_id]
                                    mark_attendance(student_id, student_info)
                                    marked.add(student_id)
                                    print(f"Marked: {student_id} - {student_info['name']}")
                        
                        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                    
                    cv2.imshow("Face Attendance - Press Q to Quit", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                cap.release()
                cv2.destroyAllWindows()
            except Exception as e:
                messagebox.showerror("Error", f"Face Attendance failed: {str(e)}")
            finally:
                self.camera_active = False
                self.update_status("Face Attendance Stopped")
        
        thread = threading.Thread(target=run_face_attendance)
        thread.daemon = True
        thread.start()
        
    def view_attendance(self):
        if not os.path.isfile(ATTENDANCE_CSV):
            messagebox.showinfo("Info", "No attendance records found!")
            return
        
        view_window = tk.Toplevel(self.root)
        view_window.title("Attendance Records")
        view_window.geometry("900x500")
        view_window.configure(bg=BG_COLOR)
        
        # Title
        title_frame = tk.Frame(view_window, bg=BG_COLOR)
        title_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(
            title_frame,
            text="Attendance Records",
            font=("Arial", 16, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        ).pack(side=tk.LEFT, padx=20)
        
        # Refresh button
        refresh_btn = tk.Button(
            title_frame,
            text="🔄 Refresh",
            command=lambda: self.refresh_attendance_view(tree),
            font=("Arial", 10),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.RIGHT, padx=20)
        
        # Record count label
        count_label = tk.Label(
            view_window,
            text="",
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        count_label.pack()
        
        # Create Treeview
        tree_frame = tk.Frame(view_window, bg=BG_COLOR)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)
        
        # Load data
        self.load_attendance_data(tree, count_label)
        
        # Add export button
        btn_frame = tk.Frame(view_window, bg=BG_COLOR)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="📂 Open Attendance Folder",
            command=lambda: self.open_folder(os.path.dirname(os.path.abspath(ATTENDANCE_CSV))),
            font=("Arial", 11),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Auto-Refresh (ON)",
            command=lambda: self.toggle_auto_refresh(view_window, tree, count_label),
            font=("Arial", 11),
            bg="#4CAF50",
            fg=BUTTON_FG,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
    
    def load_attendance_data(self, tree, count_label=None):
        """Load attendance data into the treeview"""
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            with open(ATTENDANCE_CSV, newline="", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                
                # Setup columns based on what's available
                if 'course' in fieldnames and 'email' in fieldnames:
                    tree['columns'] = ('ID', 'Name', 'Course', 'Email', 'Date', 'Time')
                    tree.column('#0', width=0, stretch=tk.NO)
                    tree.column('ID', anchor=tk.W, width=100)
                    tree.column('Name', anchor=tk.W, width=150)
                    tree.column('Course', anchor=tk.W, width=150)
                    tree.column('Email', anchor=tk.W, width=180)
                    tree.column('Date', anchor=tk.W, width=120)
                    tree.column('Time', anchor=tk.W, width=100)
                    
                    tree.heading('ID', text='Student ID', anchor=tk.W)
                    tree.heading('Name', text='Name', anchor=tk.W)
                    tree.heading('Course', text='Course', anchor=tk.W)
                    tree.heading('Email', text='Email', anchor=tk.W)
                    tree.heading('Date', text='Date', anchor=tk.W)
                    tree.heading('Time', text='Time', anchor=tk.W)
                else:
                    # Old format without course and email
                    tree['columns'] = ('ID', 'Name', 'Date', 'Time')
                    tree.column('#0', width=0, stretch=tk.NO)
                    tree.column('ID', anchor=tk.W, width=120)
                    tree.column('Name', anchor=tk.W, width=250)
                    tree.column('Date', anchor=tk.W, width=150)
                    tree.column('Time', anchor=tk.W, width=150)
                    
                    tree.heading('ID', text='Student ID', anchor=tk.W)
                    tree.heading('Name', text='Name', anchor=tk.W)
                    tree.heading('Date', text='Date', anchor=tk.W)
                    tree.heading('Time', text='Time', anchor=tk.W)
                
                # Load data
                f.seek(0)  # Reset file pointer
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    if 'course' in fieldnames and 'email' in fieldnames:
                        tree.insert('', tk.END, values=(
                            row.get('student_id', ''),
                            row.get('name', ''),
                            row.get('course', ''),
                            row.get('email', ''),
                            row.get('date', ''),
                            row.get('time', '')
                        ))
                    else:
                        tree.insert('', tk.END, values=(
                            row.get('student_id', ''),
                            row.get('name', ''),
                            row.get('date', ''),
                            row.get('time', '')
                        ))
                    row_count += 1
                
                # Update count label if provided
                if count_label:
                    count_label.config(text=f"Total Records: {row_count}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance records:\n{str(e)}")
    
    def refresh_attendance_view(self, tree, count_label=None):
        """Manually refresh the attendance view"""
        self.load_attendance_data(tree, count_label)
        self.update_status("Attendance records refreshed")
    
    def toggle_auto_refresh(self, window, tree, count_label):
        """Toggle auto-refresh for attendance view"""
        if not hasattr(self, 'auto_refresh_active'):
            self.auto_refresh_active = False
        
        self.auto_refresh_active = not self.auto_refresh_active
        
        if self.auto_refresh_active:
            self.start_auto_refresh(window, tree, count_label)
        else:
            self.stop_auto_refresh()
        
    def toggle_auto_refresh(self, window, tree, count_label):
        """Toggle auto-refresh for attendance view"""
        if not hasattr(self, 'auto_refresh_active'):
            self.auto_refresh_active = False
        
        self.auto_refresh_active = not self.auto_refresh_active
        
        if self.auto_refresh_active:
            self.start_auto_refresh(window, tree, count_label)
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self, window, tree, count_label):
        """Start auto-refreshing the attendance view every 3 seconds"""
        if hasattr(self, 'refresh_job'):
            self.root.after_cancel(self.refresh_job)
        
        def refresh_loop():
            if self.auto_refresh_active and window.winfo_exists():
                self.load_attendance_data(tree, count_label)
                self.refresh_job = self.root.after(3000, refresh_loop)  # Refresh every 3 seconds
        
        refresh_loop()
    
    def stop_auto_refresh(self):
        """Stop auto-refreshing"""
        if hasattr(self, 'refresh_job'):
            self.root.after_cancel(self.refresh_job)
        
    def exit_app(self):
        if self.camera_active:
            messagebox.showwarning("Warning", "Please stop camera operations first!")
            return
        self.root.quit()

# Main 

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartAttendanceGUI(root)
    root.mainloop()