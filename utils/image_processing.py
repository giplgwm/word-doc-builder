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

        # Create a new image with the target size and paste the resized image
        new_img = Image.new("RGB", (target_width, target_height), (255, 255, 255))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        new_img.paste(img_resized, (paste_x, paste_y))

        return new_img
