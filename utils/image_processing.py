from PIL import Image

def resize_image(image_path, target_width, target_height):
    with Image.open(image_path) as img:
        # Calculate the aspect ratio
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # Image is wider, so we'll resize based on width
            new_width = target_width
            new_height = int(new_width / img_ratio)
        else:
            # Image is taller, so we'll resize based on height
            new_height = target_height
            new_width = int(new_height * img_ratio)

        # Resize the image
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)

        return img_resized
