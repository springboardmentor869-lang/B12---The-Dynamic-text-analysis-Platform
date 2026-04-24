import os
from core.config import OUTPUT_DIR

def save_text_file(text, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    name = filename.split(".")[0]
    path = os.path.join(OUTPUT_DIR, f"{name}.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return path