from PIL import Image, ImageDraw, ImageFont

def create_sample_image(name, text, font_path, dimx, dimy):
    # create a blank image
    img = Image.new("RGB", (dimx, dimy), "white")
    draw = ImageDraw.Draw(img)

    # load the font
    font = ImageFont.truetype(font_path, 100)  # Adjust size as needed

    # get text size, center text, and draw
    text_size = draw.textbbox((0, 0), text, font=font)
    text_x = (dimx - (text_size[2] - text_size[0])) // 2
    text_y = (dimy - (text_size[3] - text_size[1])) // 2
    draw.text((text_x, text_y), text, fill="black", font=font)

    # Save or display
    img.save(name)