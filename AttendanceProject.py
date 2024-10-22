

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import  QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication,QPlainTextEdit
import openpyxl  

now = datetime.now()

dtString = now.strftime("%H:%M")


path = r'C:\Users\Admin\PycharmProjects\face_detection\face_detection\images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)


        

def findEncodings(images):
    encodeList =[]
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    attendance_file_path = 'Attendance.csv'

    # Create the file if it doesn't exist
    if not os.path.isfile(attendance_file_path):
        with open(attendance_file_path, 'w', newline='') as f:
            f.write('Name,Time,Date\n')

def is_username_unique(sheet, username):
    for row in sheet.iter_rows(values_only=True):
        if row[0] == username:
            return False
    return True

def is_late_or_ontime(current_time_str, target_time_str, lateness_threshold_minutes):
    try:
        # Parse the current time and target time strings into datetime objects
        current_time = datetime.strptime(current_time_str, '%H:%M')
        target_time = datetime.strptime(target_time_str, '%H:%M')

        # Calculate the time difference between current time and target time
        time_difference = current_time - target_time

        # Convert the time difference to minutes
        lateness_minutes = time_difference.total_seconds() / 60

        # Check if the lateness is greater than or equal to the specified threshold
        if lateness_minutes >= lateness_threshold_minutes:
            return "Late"
        else:
            return "On Time"
    except ValueError:
        return "Invalid time format. Use 'HH:MM' format (e.g., '13:45')."

#Open the file in read and write mode ('r+' or 'a' for append)
def markAttendance(name):    
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
             entry = line.split(',')
             nameList.append(entry[0])
        if name not in nameList:
            time_now = datetime.now()
            tString = time_now.strftime('%H:%M:%S')
            dString = time_now.strftime('%d/%m/%Y')
            f.writelines(f'\n{name},{tString},{dString}')
    
def main(user_input):
    workbook, sheet = markAttendance()

    # Add column headers if the sheet is empty
    if sheet.max_row == 1:
        sheet.append(["name", " Date", "Current Time", "Mark"])

    user_data = set()  # To store unique usernames

    # Check if the username is unique in the sheet
    if is_username_unique(sheet, user_input):
        user_data.add(user_input)
        current_time_str = dtString
        target_time_str = '13.44'
        lateness_threshold_minutes = 6
        result = is_late_or_ontime(current_time_str, target_time_str, lateness_threshold_minutes)
        print(result) 
        # Get the current date and time
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        # Append user input, current date, and current time to the next row
        sheet.append([user_input, current_date, current_time,result])

        workbook.save(f"{current_date}.xlsx")  # Save the workbook after each update

        # Call markAttendance function with the user's name
        markAttendance(user_input)
    else:
        print("Username already exists. Please enter a unique username.")

    
        # Check if the username is unique in the sheet
    if is_username_unique(sheet, user_input):
            user_data.add(user_input)
            current_time_str = dtString
            target_time_str = '13.44'
            lateness_threshold_minutes = 6
            result = is_late_or_ontime(current_time_str, target_time_str, lateness_threshold_minutes)
            print(result) 
            # Get the current date and time
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")

            # Append user input, current date, and current time to the next row
            sheet.append([user_input, current_date, current_time,result])
            


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

class FaceRecognitionApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

def init_ui(self):

        self.info_display = QPlainTextEdit(self)
        self.info_display.setReadOnly(True)
        self.info_display.setPlainText(str( """ This is a face recognition app if data comes as unknown please add your face by clicking on capture image button in the bottom """))
        # self.info_display.setFixedSize(400, 100) 
        # self.info_display.setFixedWidth(400)
        self.info_display.setMaximumHeight(45)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.info_display)
        self.setLayout(layout)

    # Set up the main window
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Face Recognition App')
        self.show()

    # Call update_video_frame here after the UI setup
        self.update_video_frame()
    

def update_video_frame(self):
        # Capture frame-by-frame
        ret, frame = self.video_capture.read()

        # Convert the frame from BGR color to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and their encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)


while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
        else:
            name = 'Unknown'

        print(name)
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 250, 0), cv2.FILLED)
        cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        markAttendance(name)

        # Call markAttendance function with the user's name
        markAttendance(name)
            
    cv2.imshow('FaceRecognition App', img)
    if cv2.waitKey(10) == 13:
        break
cap.release()
cv2.destroyAllWindow()

# Create an instance of the FaceRecognitionApp class
app = QtWidgets.QApplication([])
window = FaceRecognitionApp()
app.exec_()


