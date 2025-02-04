import torch
from transformers import AutoTokenizer, AutoModel
from PIL import Image
import torchvision.transforms as T

import torch
from transformers import AutoTokenizer, AutoModel
from PIL import Image
import torchvision.transforms as T

class KKLC_OCR:
    def __init__(self, model_path="OpenGVLab/InternVL2_5-1B"):
        self.model = AutoModel.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            use_flash_attn=False,
            trust_remote_code=True
        ).eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.transform = self._build_transform()

    def _build_transform(self, input_size=448):
        return T.Compose([
            T.Lambda(lambda img: img.convert('RGB')),
            T.Resize((input_size, input_size)),
            T.ToTensor(),
            T.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])

    def process_image(self, image_path):
        image = Image.open(image_path)
        pixel_values = self.transform(image).unsqueeze(0)
        question = """<image>
        What text do you see in this image? 
        Respond with only the text.
        Read the kanji characters in their Japanese form (not simplified Chinese).
        """
        return self.model.chat(self.tokenizer, pixel_values, question, dict(max_new_tokens=1024))