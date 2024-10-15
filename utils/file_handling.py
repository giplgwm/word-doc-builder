import os
import hashlib
from PIL import Image, ImageOps
import io
import extract_msg

UPLOAD_DIR = 'uploaded_files'

def save_uploaded_file(uploaded_file, filename=None):
    """
    Save the uploaded file to a permanent directory, rotate it according to EXIF data,
    and return the file path and MD5 hash.
    """
    # Calculate MD5 hash of the file content
    if isinstance(uploaded_file, io.BytesIO):
        file_content = uploaded_file.getvalue()
    else:
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
    
    md5_hash = hashlib.md5(file_content).hexdigest()

    # Create a permanent directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Determine file extension
    if filename:
        file_extension = os.path.splitext(filename)[1].lower()
    elif hasattr(uploaded_file, 'name'):
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    else:
        file_extension = '.jpg'  # Default to .jpg if no extension is available

    # Generate a unique filename using the MD5 hash
    unique_filename = f"{md5_hash}{file_extension}"

    # Save the file
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Open the image using PIL
    with Image.open(uploaded_file) as img:
        # Rotate the image according to EXIF data
        img_rotated = ImageOps.exif_transpose(img)

        # Save the rotated image
        img_rotated.save(file_path)

    print(f"File saved: {file_path}")
    return file_path, md5_hash

def extract_images_from_msg(msg_file):
    """
    Extract images from an Outlook .msg file.
    """
    msg = extract_msg.Message(msg_file)
    images = []

    for attachment in msg.attachments:
        if attachment.longFilename and attachment.longFilename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_data = io.BytesIO(attachment.data)
            images.append((image_data, attachment.longFilename))

    return images
