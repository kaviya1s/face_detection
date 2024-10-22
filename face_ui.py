import sys
import cv2
import face_recognition
import os
from datetime import datetime
from PIL import Image
import piexif
from PyQt5 import QtWidgets, QtGui, QtCore

class FaceRecognitionApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Load faces and names from the "faces" directory
        self.known_encodings, self.known_names = self.load_faces_from_directory(".faces")

        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)

        # Set up UI
        self.init_ui()

    def init_ui(self):
        # Create QLabel to display video
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)

        # Create QVBoxLayout to hold the QLabel
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.video_label)

        # Set the main layout for the QWidget
        self.setLayout(layout)

        # Set up timer to update video frames
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)
        self.timer.start(30)  # 30 milliseconds per frame

        # Set up key event handling
        self.keyPressEvent = self.on_key_press

        # Set up the main window
        self.setGeometry(100, 100, 640, 480)
        self.setWindowTitle('Face Recognition App')
        self.show()

    def load_faces_from_directory(self, faces):
        face_encodings = []
        face_names = []

        for filename in os.listdir(r"C:\Users\Admin\PycharmProjects\face_detection\face_detection\.faces"):
            # if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            if filename.lower().endswith((".jpg", ".JPG", ".jpeg", ".JPEG")):
                person_name = self.read_person_name_from_metadata(os.path.join(faces, filename))

                if person_name:
                    print(f"Person's name in {filename}: {person_name}")
                    name = person_name
                else:
                    print(f"No name exists in {filename} so using file name")
                    name = os.path.splitext(filename)[0]
                image_path = os.path.join(faces, filename)
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
            print(f"Error reading image {image_path}: {e}")

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

    def on_key_press(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Q:
            self.close()
        elif key == QtCore.Qt.Key_C:
            self.capture_photo_and_save()

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
        save_path = os.path.join("faces", filename)
        cv2.imwrite(save_path, image)
        print("Image saved")

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
            print("Metadata saved into image")
        except Exception as e:
            print(f"Error processing image {filename}: {e}")

    def closeEvent(self, event):
        self.video_capture.release()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = FaceRecognitionApp()
    sys.exit(app.exec_())
