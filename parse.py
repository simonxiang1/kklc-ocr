import torch
from transformers import AutoTokenizer, AutoModel
from PIL import Image
import torchvision.transforms as T


def build_transform(input_size=448):
    return T.Compose([
        T.Lambda(lambda img: img.convert('RGB')),
        T.Resize((input_size, input_size)),
        T.ToTensor(),
        T.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])


# load model and tokenizer
path = "OpenGVLab/InternVL2_5-1B"
model = AutoModel.from_pretrained(
    path,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
    use_flash_attn=False,
    trust_remote_code=True
).eval()
tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)


# preprocess image
image = Image.open('inputs/kanji_image.jpg')
transform = build_transform()
pixel_values = transform(image).unsqueeze(0)

# run inference
question = '<image>\nWhat text do you see in this image?'
response = model.chat(tokenizer, pixel_values, question, dict(max_new_tokens=1024))
print(response)