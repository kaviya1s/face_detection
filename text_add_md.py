from PIL import Image, ExifTags
import os
import piexif

def add_person_name_to_metadata(directory, person_name):
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            image_path = os.path.join(directory, filename)

            try:
                # Open the image to access and modify metadata
                img = Image.open(image_path)
                
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
                img.save(image_path, "JPEG", exif=exif_bytes)
            except Exception as e:
                print(f"Error processing image {filename}: {e}")


if __name__ == "__main__":
    directory_path = "faces"  # Specify the path to your image folder
    person_name_to_add = "John Doe"  # Specify the person's name to add to the metadata

    add_person_name_to_metadata(directory_path, person_name_to_add)
