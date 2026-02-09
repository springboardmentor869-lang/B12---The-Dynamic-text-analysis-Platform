from docling.document_converter import DocumentConverter

# 1️⃣ Path to document
SOURCE_FILE = "documents/American Customs And Traditions-www.learnenglishteam.com.pdf"

# 2️⃣ Create converter
converter = DocumentConverter()

# 3️⃣ Convert document
result = converter.convert(SOURCE_FILE)

# 4️⃣ Export results
markdown_text = result.document.export_to_markdown()

# 5️⃣ Save output
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_text)

print("✅ Document processed successfully")
