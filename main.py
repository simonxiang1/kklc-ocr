from src.model import KKLC_OCR
from src.sample_image import create_sample_image

def main():
    print("Hello from KKLC-OCR!")

    # creating sample images
    font_path = "/Users/simon/Library/Fonts/Hiragana-Mincho-ProN.ttc"
    save_path = "/Users/simon/coding/KKLC_OCR/data/"
    im1 = save_path + "kanji.jpg"
    im2 = save_path + "stitch.jpg"
    create_sample_image(im1, "漢字", font_path, 488, 488)
    create_sample_image(im2, "縫う", font_path, 488, 488)

    # initializing model
    ocr = KKLC_OCR()  
    print(ocr.process_image(im1))
    print(ocr.process_image(im2))


if __name__ == "__main__":
    main()
