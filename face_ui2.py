import sys
import cv2
import face_recognition
import os
from datetime import datetime
from PIL import Image
import piexif
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import  QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication,QPlainTextEdit
import logging


class LogEmitter(QObject):
    log_updated = pyqtSignal(str)

class FaceRecognitionApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.log_text_edit = QPlainTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        self.log_emitter = LogEmitter()
        self.log_emitter.log_updated.connect(self.update_log)

        # Load faces and names from the "faces" directory
        #self.known_encodings, self.known_names = self.load_faces_from_directory(".faces")
        faces_directory = os.path.join(os.getcwd(), ".faces")
        self.known_encodings, self.known_names = self.load_faces_from_directory(faces_directory)


        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)

        # Set up UI
        self.init_ui()
        self.setup_logging()
        self.last_attendance_recorded = {}
        self.load_attendance_data()

    def init_ui(self):

        self.info_display = QPlainTextEdit(self)
        self.info_display.setReadOnly(True)
        self.info_display.setPlainText(str( """ This is a face recognition app if data comes as unknown please add your face by clicking on capture image button in the bottom """))
        # self.info_display.setFixedSize(400, 100) 
        # self.info_display.setFixedWidth(400)
        self.info_display.setMaximumHeight(45)
        
        # Create QLabel to display video
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)

        # Create QPushButton for capturing photos
        self.capture_button = QtWidgets.QPushButton('Capture Photo', self)
        self.capture_button.setStyleSheet("background-color: #2ecc71; color: white; font-size: 16px;")
        self.capture_button.clicked.connect(self.capture_photo_and_save)

         # Create QPushButton for deleting a person's photo
        self.delete_button = QtWidgets.QPushButton('Delete Photo', self)
        self.delete_button.setStyleSheet("background-color: #e74c3c; color: white; font-size: 16px;")
        self.delete_button.clicked.connect(self.delete_person_photo)

        # Create QPushButton for editing person details
        self.edit_button = QtWidgets.QPushButton('Edit Details', self)
        self.edit_button.setStyleSheet("background-color: #3498db; color: white; font-size: 16px;")
        self.edit_button.clicked.connect(self.edit_person_details)

        # self.log_text_edit = QPlainTextEdit(self)
        # self.log_text_edit.setReadOnly(True)

        # Create QVBoxLayout to hold the QLabel and QPushButton
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.info_display)
        layout.addWidget(self.video_label)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.log_text_edit)
        
        # Set the main layout for the QWidget
        self.setLayout(layout)

        # Set up timer to update video frames
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)
        self.timer.start(30)  # 30 milliseconds per frame

        # Set up the main window
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Face Recognition App')
        self.show()

        # self.log_emitter = LogEmitter()
        # self.log_emitter.log_updated.connect(self.update_log)

    def setup_logging(self):
    
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        self.logger = logging.getLogger('ApplicationLogger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(stream_handler)

    def update_log(self, message):
        print(message)
        self.log_text_edit.appendPlainText(message)  
        QApplication.processEvents() 

    def load_faces_from_directory(self, directory):
        log_message = f"Loading all the photos saved in the application"
        self.log_emitter.log_updated.emit(log_message)
        face_encodings = []
        face_names = []

        for filename in os.listdir(directory):
            if filename.lower().endswith((".jpg", ".jpeg")):
                person_name = self.read_person_name_from_metadata(os.path.join(directory, filename))

                if person_name:
                    # print(f"Person's name in {filename}: {person_name}")
                    log_message = f"Person's name in {filename}: {person_name}"
                    self.log_emitter.log_updated.emit(log_message)
                    name = person_name
                else:
                    # print(f"No name exists in {filename} so using file name")
                    log_message = f"No name exists in {filename} so using file name"
                    self.log_emitter.log_updated.emit(log_message)
                    name = os.path.splitext(filename)[0]
                image_path = os.path.join(directory, filename)
                face_image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(face_image)[0]
                face_encodings.append(face_encoding)
                face_names.append(name)

        return face_encodings, face_names

    def read_person_name_from_metadata(self, image_path):
        try:
            # Open the image to access metadata
            img = Image.open(image_path)

            # Check if Exif data exists
            exif_data = img.info.get("exif", b"")
            if exif_data:
                # Get the existing Exif data
                exif_dict = piexif.load(exif_data)
                # Extract artist information (person's name) from Exif data
                artist_name = exif_dict['0th'].get(piexif.ImageIFD.Artist, b"").decode('utf-8')

                if artist_name:
                    return artist_name
        except Exception as e:
            # print(f"Error reading image {image_path}: {e}")
            log_message = f"Error reading image {image_path}: {e}"
            self.log_emitter.log_updated.emit(log_message)

        return None

    def update_video_frame(self):
        # Capture frame-by-frame
        ret, frame = self.video_capture.read()

        # Convert the frame from BGR color to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and their encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face detected in the frame
        for face_encoding in face_encodings:
            # Compare the face encoding with the known encodings
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            name = "Unknown"

            # Check if there is a match
            if True in matches:
                # Find the indexes of all matched faces and count their occurrences
                matched_indexes = [i for (i, match) in enumerate(matches) if match]
                counts = {}

                # Count the occurrences of each matched face
                for index in matched_indexes:
                    counts[self.known_names[index]] = counts.get(self.known_names[index], 0) + 1

                # Find the name with the maximum count
                name = max(counts, key=counts.get)
                self.record_attendance(name)

            # Draw a rectangle around the face and display the name
            top, right, bottom, left = face_recognition.face_locations(rgb_frame)[0]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Display the resulting image in the UI
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QtGui.QImage(frame.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)

    def capture_photo_and_save(self):
        # Capture a single frame
        ret, frame = self.video_capture.read()

        # Prompt user for person's name
        file_name, ok = QtWidgets.QInputDialog.getText(self, 'File Name', 'Enter the file name to save:')
        person_name, ok = QtWidgets.QInputDialog.getText(self, 'Person Name', 'Enter the person\'s name:')

        # Generate a filename based on the provided file name or timestamp
        saved_name = f"{file_name}.jpg" if file_name else datetime.now().strftime("%Y%m%d%H%M%S.jpg")

        # Save the image with metadata
        self.save_image_with_metadata(frame, saved_name, person_name)

    def save_image_with_metadata(self, image, filename, person_name):
        # Save the image in the "faces" directory
        save_path = os.path.join(".faces", filename)
        cv2.imwrite(save_path, image)
        # print("Image saved")
        log_message = f"Image saved"
        self.log_emitter.log_updated.emit(log_message)

        try:
            # Open the image to access and modify metadata
            img = Image.open(save_path)

            # Check if Exif data exists
            exif_data = img.info.get("exif", b"")
            if exif_data:
                # Get the existing Exif data
                exif_dict = piexif.load(exif_data)
            else:
                exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}

            # Add person's name to the Exif data
            exif_dict['0th'][piexif.ImageIFD.Artist] = person_name

            # Convert the Exif data back to bytes
            exif_bytes = piexif.dump(exif_dict)

            # Save the modified metadata back to the image
            img.save(save_path, "JPEG", exif=exif_bytes)
            # print("Metadata saved into image")
            log_message = f"Metadata saved into image"
            self.log_emitter.log_updated.emit(log_message)
            self.known_encodings, self.known_names = self.load_faces_from_directory(".faces")
        except Exception as e:
            # print(f"Error processing image {filename}: {e}")
            log_message = f"Error processing image {filename}: {e}"
            self.log_emitter.log_updated.emit(log_message)

    def delete_person_photo(self):
        person_name, ok = QtWidgets.QInputDialog.getText(self, 'Delete Photo', 'Enter the person\'s name to delete photo:')
        if ok and person_name:
            for filename in os.listdir(".faces"):
                if filename.lower().endswith((".jpg", ".jpeg")):
                    existing_name = self.read_person_name_from_metadata(os.path.join(".faces", filename))
                    if existing_name == person_name:
                        os.remove(os.path.join(".faces", filename))
                        self.log_emitter.log_updated.emit(f"Deleted photo for {person_name}")
                        self.known_encodings, self.known_names = self.load_faces_from_directory(".faces")
                        return

            self.log_emitter.log_updated.emit(f"No photo found for {person_name}")

    def edit_person_details(self):
        person_name, ok = QtWidgets.QInputDialog.getText(self, 'Edit Details', 'Enter the person\'s name to edit details:')
        if ok and person_name:
            for filename in os.listdir(".faces"):
                if filename.lower().endswith((".jpg", ".jpeg")):
                    existing_name = self.read_person_name_from_metadata(os.path.join(".faces", filename))
                    if existing_name == person_name:
                        new_name, ok = QtWidgets.QInputDialog.getText(self, 'Edit Details', 'Enter the new name:')
                        if ok:
                            self.save_image_with_metadata(cv2.imread(os.path.join(".faces", filename)), filename, new_name)
                            self.log_emitter.log_updated.emit(f"Details updated for {person_name}")
                            self.known_encodings, self.known_names = self.load_faces_from_directory(".faces")
                            return

            self.log_emitter.log_updated.emit(f"No details found for {person_name}")

    def load_attendance_data(self):
        #self.attendance_file_path = "attendance.csv"
        #self.attendance_file_path = os.path.join(os.getcwd(), "attendance.csv")
        self.attendance_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.csv")
        if not os.path.exists(self.attendance_file_path):
            print("Attendance file path:", self.attendance_file_path)


        if not os.path.exists(self.attendance_file_path):
            with open(self.attendance_file_path, 'w') as f:
                f.write("Name,Date&Time\n")
                f.close()

    now = datetime.now()

    def record_attendance(self, person_name):
        # Check if the person's attendance has been recorded in the last hour
        if not self.is_attendance_recorded_recently(person_name):
            # Record attendance
            date_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.attendance_file_path, 'a') as f:
               f.write(f"{person_name},{date_time_str}\n")
            log_message = f"Attendance recorded for {person_name}"
            self.log_emitter.log_updated.emit(f"Attendance recorded for {person_name}")
            #Update the last recorded time for the person
            self.last_attendance_recorded[person_name] = datetime.now()
        else:
            #Attendance already recorded within the last hour
            log_message = f"Attendance already recorded for {person_name} within the last hour. Come back later."
        self.log_emitter.log_updated.emit(log_message)

    def is_attendance_recorded_recently(self, person_name):
        # Check if the person's attendance has been recorded in the last hour
        if person_name in self.last_attendance_recorded:
            last_recorded_time = self.last_attendance_recorded[person_name]
            current_time = datetime.now()
            time_difference = current_time - last_recorded_time
            return time_difference.total_seconds() < 3600  # 3600 seconds = 1 hour
        else:
            return False

    def closeEvent(self, event):
        self.video_capture.release()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = FaceRecognitionApp()
    sys.exit(app.exec_())
