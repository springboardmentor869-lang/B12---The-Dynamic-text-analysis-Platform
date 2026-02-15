import os
from parsers.document_parser import extract_pdf, extract_docx

INPUT_FOLDER = "data"
OUTPUT_FOLDER = "output"

def start_conversion():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]
    print(f"Checking data folder... Found {len(files)} files.")

    for file in files:
        input_path = os.path.join(INPUT_FOLDER, file)
        output_name = os.path.splitext(file)[0] + ".txt"
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        if file.lower().endswith(".pdf"):
            print(f"Converting PDF: {file}")
            content = extract_pdf(input_path)
        elif file.lower().endswith(".docx"):
            print(f"Converting DOCX: {file}")
            content = extract_docx(input_path)
        else:
            continue

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {output_name}")

if __name__ == "__main__":
    start_conversion()