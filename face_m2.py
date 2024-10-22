import cv2
import face_recognition
import os

# Function to load faces and corresponding names from a directory
def load_faces_from_directory(directory):
    face_encodings = []
    face_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".JPG") or filename.endswith(".JPEG"):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(directory, filename)
            face_image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(face_image)[0]
            face_encodings.append(face_encoding)
            face_names.append(name)

    return face_encodings, face_names

# Load faces and names from the "faces" directory
known_encodings, known_names = load_faces_from_directory("faces")

# Initialize video capture
video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Convert the frame from BGR color to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop through each face detected in the frame
    for face_encoding in face_encodings:
        # Compare the face encoding with the known encodings
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        # Check if there is a match
        if True in matches:
            # Find the indexes of all matched faces and count their occurrences
            matched_indexes = [i for (i, match) in enumerate(matches) if match]
            counts = {}

            # Count the occurrences of each matched face
            for index in matched_indexes:
                counts[known_names[index]] = counts.get(known_names[index], 0) + 1

            # Find the name with the maximum count
            name = max(counts, key=counts.get)

        # Draw a rectangle around the face and display the name
        top, right, bottom, left = face_recognition.face_locations(rgb_frame)[0]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the window
video_capture.release()
cv2.destroyAllWindows()
