import cv2
import face_recognition
import os
from datetime import datetime
from PIL import Image
import piexif

def read_person_name_from_metadata(image_path):
    try:
        # Open the image to access metadata
        img = Image.open(image_path)

        # Check if Exif data exists
        exif_data = img.info.get("exif", b"")
        if exif_data:
            # Get the existing Exif data
            exif_dict = piexif.load(exif_data)
            # print(f"exif_dict is {exif_data} \n \n \n new line {exif_dict}")
            # Extract artist information (person's name) from Exif data
            artist_name = exif_dict['0th'].get(piexif.ImageIFD.Artist, b"").decode('utf-8')
            # print(f"artist name {artist_name}")
            
            if artist_name:
                return artist_name
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
    
    return None

# Function to load faces and corresponding names from a directory
def load_faces_from_directory(directory):
    face_encodings = []
    face_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            person_name = read_person_name_from_metadata(os.path.join(directory,filename))

            if person_name:
                print(f"Person's name in {filename}: {person_name}")
                name = person_name
            else:
                print(f"No name exists in {filename} so using file name")
                name = os.path.splitext(filename)[0]
            image_path = os.path.join(directory, filename)
            face_image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(face_image)[0]
            face_encodings.append(face_encoding)
            face_names.append(name)

    return face_encodings, face_names

# Function to save image with metadata
def save_image_with_metadata(image, filename, person_name):
    # Save the image in the "faces" directory
    save_path = os.path.join("faces", filename)
    cv2.imwrite(save_path, image)
    print("image saved")

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
        print("metadata saved into image")
    except Exception as e:
        print(f"Error processing image {filename}: {e}")


# Function to capture photo and save with metadata
def capture_photo_and_save(video_capture):
    # Capture a single frame
    ret, frame = video_capture.read()

    # Convert the frame from BGR color to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Display the image for a moment
    cv2.imshow("Captured Photo", cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
    cv2.waitKey(1000)
    cv2.destroyWindow("Captured Photo")

    # Prompt user for person's name
    print("Image captured\n")
    file_name = input("Enter the file name to save: ")
    person_name = input("Enter the person's name: ")

    # Generate a filename based on current timestamp
    # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_name = f"{file_name}.jpg"

    # Save the image with metadata
    save_image_with_metadata(frame, saved_name, person_name)

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

    # Check for key press events
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        capture_photo_and_save(video_capture)

# Release the video capture and close the window
video_capture.release()
cv2.destroyAllWindows()
