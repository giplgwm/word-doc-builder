import streamlit as st
from PIL import Image
import io
from utils.image_processing import crop_image
from utils.document_generation import create_word_document, create_pdf_document
from utils.file_handling import save_uploaded_file

st.set_page_config(
    page_title="Word Doc Builder",
    page_icon="📝",
    menu_items={'About': "Generates word documents with photos & labels, with page breaks between them."}
)

# Initialize session state
if 'photos' not in st.session_state:
    st.session_state.photos = []

# File uploader
uploaded_files = st.file_uploader("Upload photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files:
    new_files_added = False
    for uploaded_file in uploaded_files:
        # Save the uploaded file and get the file path and MD5 hash
        file_path, md5_hash = save_uploaded_file(uploaded_file)
        
        # Check if the file is already in the session state
        if not any(photo['md5_hash'] == md5_hash for photo in st.session_state.photos):
            # Add the file path, MD5 hash, and an empty label to the session state
            st.session_state.photos.append({"path": file_path, "md5_hash": md5_hash, "label": "", "name": uploaded_file.name})
            new_files_added = True
    
    if new_files_added:
        st.success("New files have been uploaded successfully!")
    else:
        pass

# Display info message
if st.session_state.photos:
    st.text("You can label and reorder your photos below. Photos with no label will be labeled the same as the photo before them, so you don't have to repeat yourself.")

# Display and label photos
if st.session_state.photos:
    # Add "Move Up" and "Move Down" buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Move Up"):
            selected_indices = [i for i, photo in enumerate(st.session_state.photos) if st.session_state.get(f"select_{i}", False)]
            for idx in sorted(selected_indices):
                if idx > 0:
                    # Swap photos
                    st.session_state.photos[idx], st.session_state.photos[idx-1] = st.session_state.photos[idx-1], st.session_state.photos[idx]
            st.rerun()  # Add this line to refresh the page after moving photos
    
    with col2:
        if st.button("Move Down"):
            selected_indices = [i for i, photo in enumerate(st.session_state.photos) if st.session_state.get(f"select_{i}", False)]
            for idx in sorted(selected_indices, reverse=True):
                if idx < len(st.session_state.photos) - 1:
                    # Swap photos
                    st.session_state.photos[idx], st.session_state.photos[idx+1] = st.session_state.photos[idx+1], st.session_state.photos[idx]
            st.rerun()  # Add this line to refresh the page after moving photos

    # Display photos and labels
    for i, photo in enumerate(st.session_state.photos):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            is_selected = st.checkbox("Select", key=f"select_{i}", value=st.session_state.get(f"select_{i}", False))
            st.image(photo["path"], use_column_width=True)
        
        with col2:
            new_label = st.text_input(f"Label for photo {i+1}", value=photo["label"], key=f"label_{i}")
            st.session_state.photos[i]["label"] = new_label

# Generate document
if st.session_state.photos:
    document_name = st.text_input("Enter document name", value="photos")
    doc_type = st.radio("Select document type", ("Word", "PDF"))
    if st.button("Generate Document"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        if doc_type == "Word":
            doc_file = create_word_document(st.session_state.photos, progress_callback=lambda p: progress_bar.progress(p))
            file_extension = "docx"
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            doc_file = create_pdf_document(st.session_state.photos, progress_callback=lambda p: progress_bar.progress(p))
            file_extension = "pdf"
            mime_type = "application/pdf"
        
        progress_bar.progress(100)
        status_text.text("Document generated successfully!")
        
        # Offer the document for download
        st.download_button(
            label="Download Document",
            data=doc_file.getvalue(),
            file_name=f"{document_name}.{file_extension}",
            mime=mime_type
        )
