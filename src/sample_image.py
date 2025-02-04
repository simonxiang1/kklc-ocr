from PIL import Image, ImageDraw, ImageFont

# create a blank image
img = Image.new("RGB", (448, 448), "white")
draw = ImageDraw.Draw(img)

# load the font
font_path = "/Users/simon/Library/Fonts/Hiragana-Mincho-ProN.ttc"
font = ImageFont.truetype(font_path, 100)  # Adjust size as needed

# get text size, center text, and draw
text = "漢字"
text_size = draw.textbbox((0, 0), text, font=font)
text_x = (448 - (text_size[2] - text_size[0])) // 2
text_y = (448 - (text_size[3] - text_size[1])) // 2
draw.text((text_x, text_y), text, fill="black", font=font)

# Save or display
img.save("../data/kanji_image.jpg")