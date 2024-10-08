import os
import tempfile
import hashlib
from PIL import Image, ImageOps

def save_uploaded_file(uploaded_file):
    """
    Save the uploaded file to a temporary directory, rotate it according to EXIF data,
    and return the file path and MD5 hash.
    """
    # Calculate MD5 hash of the file content
    md5_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()

    # Create a temporary directory if it doesn't exist
    temp_dir = tempfile.gettempdir()
    os.makedirs(temp_dir, exist_ok=True)

    # Generate a unique filename using the MD5 hash
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    unique_filename = f"{md5_hash}{file_extension}"

    # Save the file
    file_path = os.path.join(temp_dir, unique_filename)

    # Open the image using PIL
    with Image.open(uploaded_file) as img:
        # Rotate the image according to EXIF data
        img_rotated = ImageOps.exif_transpose(img)

        # Save the rotated image
        img_rotated.save(file_path)

    return file_path, md5_hash
