import io
from docx import Document
from docx.shared import Inches
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from utils.image_processing import resize_image


def create_word_document(photos, progress_callback=None):
    document = Document()
    last_label = ""

    for i, photo in enumerate(photos):
        if i > 0:
            document.add_page_break()

        img = resize_image(photo["path"], int(Inches(6).pt * 96 / 72), int(Inches(8).pt * 96 / 72))
        with io.BytesIO() as image_stream:
            img.save(image_stream, format='PNG')
            image_stream.seek(0)
            picture = document.add_picture(image_stream)
            
            # Adjust the size of the picture while maintaining aspect ratio
            aspect_ratio = picture.width / picture.height
            if aspect_ratio > 6/8:  # If the image is wider than 6x8 inches
                picture.width = Inches(6)
                picture.height = int(round(picture.width / aspect_ratio))
            else:
                picture.height = Inches(8)
                picture.width = int(round(picture.height * aspect_ratio))

        # Use the nearest label from above if current photo is unlabeled
        label = photo["label"] if photo["label"] else last_label
        last_label = label

        # Add a left-aligned paragraph for the label
        paragraph = document.add_paragraph(label)
        paragraph.alignment = 0  # 0 corresponds to left alignment

        if progress_callback:
            progress_callback((i + 1) / len(photos))

    doc_file = io.BytesIO()
    document.save(doc_file)
    doc_file.seek(0)

    return doc_file


def create_pdf_document(photos, progress_callback=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)  # 1 inch left margin
    styles = getSampleStyleSheet()
    last_label = ""

    story = []

    for i, photo in enumerate(photos):
        img = resize_image(photo["path"], 6 * 72, 8 * 72)  # 72 points per inch
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        story.append(RLImage(img_buffer, width=6 * 72, height=8 * 72))

        # Use the nearest label from above if current photo is unlabeled
        label = photo["label"] if photo["label"] else last_label
        last_label = label

        # Add left-aligned label
        label_style = styles['Normal']
        label_style.alignment = 0  # 0 corresponds to left alignment
        story.append(Paragraph(label, label_style))

        if i < len(photos) - 1:
            story.append(PageBreak())

        if progress_callback:
            progress_callback((i + 1) / len(photos))

    doc.build(story)
    buffer.seek(0)

    return buffer
