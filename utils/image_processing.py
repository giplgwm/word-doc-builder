from PIL import Image

def crop_image(image_path, target_width, target_height):
    """
    Crop the image to fit the target dimensions without changing the aspect ratio.
    """
    with Image.open(image_path) as img:
        # Calculate the aspect ratio
        aspect_ratio = min(target_width / img.width, target_height / img.height)
        
        # Calculate new dimensions
        new_width = int(img.width * aspect_ratio)
        new_height = int(img.height * aspect_ratio)
        
        # Resize the image
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Create a new image with white background
        new_img = Image.new("RGB", (target_width, target_height), (255, 255, 255))
        
        # Paste the resized image onto the center of the new image
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        new_img.paste(img_resized, (paste_x, paste_y))
        
        return new_img
