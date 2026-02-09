import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# ---------- Load text ----------
with open("../output_docs/task2pdf_sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

# ---------- 1. CLEANING ----------
cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()

# remove duplicate lines
lines = cleaned_text.splitlines()
unique_lines = list(dict.fromkeys(lines))
cleaned_text = "\n".join(unique_lines)


with open("cleaned.txt", "w", encoding="utf-8") as f:
    f.write(cleaned_text)

# ---------- 2. TOKENIZATION ----------
tokens = word_tokenize(cleaned_text)

with open("tokens.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(tokens))

# ---------- 3. STOPWORD REMOVAL ----------
stop_words = set(stopwords.words('english'))
filtered_tokens = [word for word in tokens if word not in stop_words]

with open("no_stopwords.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(filtered_tokens))

# ---------- 4. STEMMING ----------
stemmer = PorterStemmer()
stemmed_words = [stemmer.stem(word) for word in filtered_tokens]

with open("stemmed.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(stemmed_words))

# ---------- 5. LEMMATIZATION ----------
lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_tokens]

with open("lemmatized.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(lemmatized_words))

print("Preprocessing completed successfully")
