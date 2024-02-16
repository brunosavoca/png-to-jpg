import streamlit as st
from PIL import Image
import os
from concurrent.futures import ProcessPoolExecutor
import zipfile
import shutil
import streamlit as st
import streamlit_analytics


def save_as_jpeg(png_path, jpg_path):
    try:
        img = Image.open(png_path)
        rgb_im = img.convert('RGB')
        rgb_im.save(jpg_path, quality=95)  # Set a high quality value
        return f"Successfully converted {png_path} to {jpg_path}"
    except Exception as e:
        return f"Error converting {png_path}: {str(e)}"

with streamlit_analytics.track():

st.title("PNG to JPG Converter")

    uploaded_files = st.file_uploader("Choose PNG files", accept_multiple_files=True, type=['png', 'webp'])
    
    if uploaded_files:
        output_dir = "output_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
        with st.spinner("Processing..."):
            with ProcessPoolExecutor() as executor:
                futures = []
                for uploaded_file in uploaded_files:
                    png_path = os.path.join(output_dir, uploaded_file.name)
                    jpg_path = os.path.join(output_dir, os.path.splitext(uploaded_file.name)[0] + '.jpg')
                    # Saving the uploaded PNG file temporarily
                    with open(png_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
    
                    # Submitting conversion task
                    futures.append(executor.submit(save_as_jpeg, png_path, jpg_path))
    
                results = [future.result() for future in futures]
                for result in results:
                    st.write(result)
    
        # Creating a zip file with all the converted JPGs
        with zipfile.ZipFile('converted_images.zip', 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        zipf.write(os.path.join(root, file), file)
    
        # Providing the download button
        st.success("Conversion completed!")
        with open('converted_images.zip', 'rb') as file:
            bytes_data = file.read()
        st.download_button(label="Download JPG files", data=bytes_data, mime='application/zip')
    
        # Optionally, clean up by removing the output directory and zip file
        shutil.rmtree(output_dir)
        os.remove('converted_images.zip')
