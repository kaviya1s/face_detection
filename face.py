import cv2
import face_recognition

# Load a sample image and encode the known face(s)
known_image = face_recognition.load_image_file("Passport size photo.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []

# Load the video capture
video_capture = cv2.VideoCapture(0)

while True:
    # Capture each frame from the video
    ret, frame = video_capture.read()

    # Convert the frame from BGR color to RGB color
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces and their encodings in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    # print("location is",face_locations)
    face_names = []
    for face_encoding in face_encodings:
        # Compare each face encoding with the known encoding
        matches = face_recognition.compare_faces([known_encoding], face_encoding)
        name = "Unknown"

        # If there is a match, get the name of the known person
        if matches[0]:
            name = "known person"

        face_names.append(name)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # print(top,right,bottom,left)

        # Draw the name below the face
        cv2.rectangle(frame, (left, bottom - 20), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
video_capture.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
