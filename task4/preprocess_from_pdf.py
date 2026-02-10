import pdfplumber
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

text = ""

with pdfplumber.open("input_docs/report.pdf") as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "

print("PDF text extracted")

clean_text = re.sub(r'[^a-zA-Z\s]', '', text)
clean_text = clean_text.lower()

tokens = word_tokenize(clean_text)

stop_words = set(stopwords.words('english'))
filtered_tokens = [w for w in tokens if w not in stop_words]

stemmer = PorterStemmer()
stemmed_words = [stemmer.stem(w) for w in filtered_tokens]

lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(w) for w in filtered_tokens]

with open("stemmed.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(stemmed_words))

with open("lemmatized.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(lemmatized_words))

print("Preprocessing completed")
