from docling.document_converter import DocumentConverter
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

nltk.download("stopwords")
nltk.download("wordnet")

# ================= PDF → MARKDOWN =================
source = "input.pdf"
converter = DocumentConverter()
result = converter.convert(source)

markdown_text = result.document.export_to_markdown()
with open("converted.md", "w", encoding="utf-8") as f:
    f.write(markdown_text)

print("\n--- Markdown Preview ---")
print(markdown_text[:500])

# ================= READ MARKDOWN =================
with open("converted.md", "r", encoding="utf-8") as f:
    text = f.read()

print("\n--- Raw Text Preview ---")
print(text[:500])

# ================= CLEANING =================
text = text.lower()
text = re.sub(r"[^a-z\s]", " ", text)
text = re.sub(r"\s+", " ", text).strip()

print("\n--- Cleaned Text Preview ---")
print(text[:500])

# ================= TOKENIZATION =================
tokens = text.split()

print("\n--- Tokens (first 30) ---")
print(tokens[:30])
print("Total tokens:", len(tokens))

# ================= STOPWORD REMOVAL =================
stop_words = set(stopwords.words("english"))
filtered_tokens = [word for word in tokens if word not in stop_words]

print("\n--- After Stopword Removal (first 30) ---")
print(filtered_tokens[:30])
print("Total tokens after stopword removal:", len(filtered_tokens))

# ================= STEMMING =================
stemmer = PorterStemmer()
stemmed_words = [stemmer.stem(word) for word in filtered_tokens]

print("\n--- Stemmed Words (first 30) ---")
print(stemmed_words[:30])

with open("stemmed_output.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(stemmed_words))

# ================= LEMMATIZATION =================
lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_tokens]

print("\n--- Lemmatized Words (first 30) ---")
print(lemmatized_words[:30])

with open("lemmatized_output.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(lemmatized_words))

print("\nPreprocessing completed successfully.")
