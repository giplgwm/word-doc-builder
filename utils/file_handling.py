import os
import hashlib
from PIL import Image, ImageOps
import io
import extract_msg
import email
from email.header import decode_header
from streamlit.runtime.uploaded_file_manager import UploadedFile
from pillow_heif import register_heif_opener

register_heif_opener()

UPLOAD_DIR = 'uploaded_files'

def save_uploaded_file(uploaded_file, filename=None):
    """
    Save the uploaded file to a permanent directory, rotate it according to EXIF data,
    and return the file path and MD5 hash.
    """
    if isinstance(uploaded_file, io.BytesIO):
        file_content = uploaded_file.getvalue()
    else:
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
    
    md5_hash = hashlib.md5(file_content).hexdigest()

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if filename:
        file_extension = os.path.splitext(filename)[1].lower()
    elif hasattr(uploaded_file, 'name'):
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    else:
        file_extension = '.jpg'  

    unique_filename = f"{md5_hash}{file_extension}"

    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with Image.open(uploaded_file) as img:
        img_rotated = ImageOps.exif_transpose(img)
        img_rotated.save(file_path)

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

def extract_images_from_eml(eml_file):
    """
    Extract images from an .eml file.
    """
    msg = email.message_from_bytes(eml_file.read())
    images = []

    for part in msg.walk():
        if part.get_content_maintype() == 'image':
            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()
            else:
                filename = f'image_{len(images)}.jpg'

            image_data = io.BytesIO(part.get_payload(decode=True))
            images.append((image_data, filename))

    return images
