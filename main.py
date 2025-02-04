from src.model import KKLC_OCR

def main():
    print("Hello from KKLC-OCR!")

    ocr = KKLC_OCR()  
    result = ocr.process_image('data/kanji_image.jpg')
    print(result)


if __name__ == "__main__":
    main()
