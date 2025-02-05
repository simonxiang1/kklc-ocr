from src.google_cloud_api import process_scanned_pdf
import os

def main():
    print("Hello from KKLC-OCR!")
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/simon/coding/mimetic-fulcrum-450000-u4-b833a522c287.json'

    # process_scanned_pdf(
    #     "data/kklc_page.pdf",
    #     "outputs/page_output.txt"
    # ) 


if __name__ == "__main__":
    main()
