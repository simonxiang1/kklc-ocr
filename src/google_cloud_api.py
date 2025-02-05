from google.cloud import vision
from pdf2image import convert_from_path
import io

def process_scanned_pdf(pdf_path, output_path):
    """
    Process a scanned PDF by converting pages to images and performing OCR.
    
    This function handles scanned documents by:
    1. Converting PDF pages to images using pdf2image
    2. Processing each image with Google Cloud Vision's OCR
    3. Writing the extracted text to an output file
    """
    client = vision.ImageAnnotatorClient()
    print("Converting PDF to images...")
    
    try:
        # Convert PDF pages to images
        # Note: you'll need poppler installed for pdf2image to work
        pages = convert_from_path(pdf_path)
        print(f"Successfully converted {len(pages)} pages to images")
        
        with open(output_path, 'w', encoding='utf-8') as output_file:
            # Process each page
            for page_num, page_image in enumerate(pages, 1):
                print(f"Processing page {page_num}...")
                
                # Convert PIL Image to bytes for Google Cloud Vision
                img_byte_arr = io.BytesIO()
                page_image.save(img_byte_arr, format='PNG')
                content = img_byte_arr.getvalue()
                
                # Create image object for OCR
                image = vision.Image(content=content)
                
                # Perform OCR on the image
                response = client.text_detection(image=image)
                
                if response.error.message:
                    raise Exception(
                        f'Error processing page {page_num}: {response.error.message}'
                    )
                
                # Extract the text
                texts = response.text_annotations
                if texts:
                    # The first text_annotation contains all text in reading order
                    page_text = texts[0].description
                    output_file.write(page_text)
                    output_file.write('\n')
                    print(f"Successfully processed page {page_num}")
                else:
                    print(f"No text found on page {page_num}")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())