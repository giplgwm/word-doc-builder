import streamlit as st
from PIL import Image
import io
from utils.document_generation import create_word_document, create_pdf_document
from utils.file_handling import save_uploaded_file, extract_images_from_msg, extract_images_from_eml

st.set_page_config(
    page_title="Word Doc Builder",
    page_icon="📝",
    menu_items={
        'About':
        "Generates word documents with photos & labels, with page breaks between them."
    })

if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'blocked_photos' not in st.session_state:
    st.session_state.blocked_photos = []
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 1

uploaded_files = st.file_uploader("Upload photos or email files (.msg or .eml)",
                                  type=["jpg", "jpeg", "png", "msg", "eml"],
                                  accept_multiple_files=True,
                                 key=f'fileuploader_{st.session_state.file_uploader_key}')
if uploaded_files:
    new_files_added = False
    for uploaded_file in uploaded_files:
        if uploaded_file.name.lower().endswith('.msg'):
            # Extract images from .msg file
            extracted_images = extract_images_from_msg(uploaded_file)
        elif uploaded_file.name.lower().endswith('.eml'):
            # Extract images from .eml file
            extracted_images = extract_images_from_eml(uploaded_file)
        else:
            # Regular image file
            extracted_images = [(uploaded_file, uploaded_file.name)]

        for img_data, img_filename in extracted_images:
            file_path, md5_hash = save_uploaded_file(img_data, filename=img_filename)
            
            # Check if the file is not in the blocked list and not already in the session state
            if md5_hash not in st.session_state.blocked_photos and not any(
                    photo.get('md5_hash') == md5_hash
                    for photo in st.session_state.photos):
                
                st.session_state.photos.append({
                    "path": file_path,
                    "md5_hash": md5_hash,
                    "label": "",
                    "name": img_filename,
                    "selected": False
                })
                new_files_added = True

    if new_files_added:
        st.session_state.file_uploader_key += 1
        st.rerun()

if st.session_state.photos:
    st.text(
        "You can label, reorder, and edit your photos below. Photos with no label will be labeled the same as the photo before them, so you don't have to repeat yourself."
    )

if st.session_state.photos:
    st.sidebar.title("Photo Controls")
    st.sidebar.markdown("---")
    st.sidebar.write("Select images and then use the controls below to reorder or remove them")
    st.sidebar.markdown("---")
    if st.sidebar.button("Move Up"):
        selected_indices = [
            i for i, photo in enumerate(st.session_state.photos)
            if photo["selected"]
        ]
        for idx in sorted(selected_indices):
            if idx > 0:
                # Swap photos and labels
                st.session_state.photos[idx], st.session_state.photos[
                    idx - 1] = st.session_state.photos[
                        idx - 1], st.session_state.photos[idx]
                # Update selection state
                st.session_state.photos[idx]['selected'] = False
                st.session_state.photos[idx - 1]['selected'] = True
        st.rerun()

    if st.sidebar.button("Move Down"):
        selected_indices = [
            i for i, photo in enumerate(st.session_state.photos)
            if photo["selected"]
        ]
        for idx in sorted(selected_indices, reverse=True):
            if idx < len(st.session_state.photos) - 1:
                # Swap photos and labels
                st.session_state.photos[idx], st.session_state.photos[
                    idx + 1] = st.session_state.photos[
                        idx + 1], st.session_state.photos[idx]
                # Update selection state
                st.session_state.photos[idx]['selected'] = False
                st.session_state.photos[idx + 1]['selected'] = True
        st.rerun()

    if st.sidebar.button('Remove Selected'):
        selected_hashes = [photo['md5_hash'] for photo in st.session_state.photos if photo['selected']]
        
        st.session_state.blocked_photos.extend(selected_hashes)
        
        st.session_state.photos = [photo for photo in st.session_state.photos if not photo['selected']]
        
        
        st.rerun()


    for i, photo in enumerate(st.session_state.photos):
        with st.container():
            is_selected = st.checkbox("Select", key=f"select_{i}", value=photo["selected"])
            if is_selected != photo["selected"]:
                st.session_state.photos[i]["selected"] = is_selected
                st.rerun()

            display_width = 250
            st.image(photo["path"], use_column_width=False, width=display_width)

            new_label = st.text_input(f"Label for photo {i+1}", value=photo["label"], key=f"label_{i}")
            st.session_state.photos[i]["label"] = new_label

        st.markdown("---") 


if st.session_state.photos:
    document_name = st.text_input("Enter document name", value="photos")
    doc_type = st.radio("Select document type", ("Word", "PDF"))
    if st.button("Generate Document"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        if doc_type == "Word":
            doc_file = create_word_document(
                st.session_state.photos,
                progress_callback=lambda p: progress_bar.progress(p))
            file_extension = "docx"
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            doc_file = create_pdf_document(
                st.session_state.photos,
                progress_callback=lambda p: progress_bar.progress(p))
            file_extension = "pdf"
            mime_type = "application/pdf"

        progress_bar.progress(100)
        status_text.text("Document generated successfully!")

        st.download_button(label="Download Document",
                           data=doc_file.getvalue(),
                           file_name=f"{document_name}.{file_extension}",
                           mime=mime_type)
