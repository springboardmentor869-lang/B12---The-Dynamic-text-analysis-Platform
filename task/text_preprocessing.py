print("PROGRAM STARTED")

import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Read text file
with open("financial_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("\nORIGINAL TEXT:")
print(text)

# Safety check
if text.strip() == "":
    print("ERROR: financial_text.txt is empty")
    exit()

# Clean text
clean_text = re.sub(r"[^a-zA-Z\s]", "", text)
clean_text = clean_text.lower()

print("\nCLEANED TEXT:")
print(clean_text)

# Tokenization (NO punkt dependency)
tokens = clean_text.split()
print("\nTOKENS:")
print(tokens)

# Remove stopwords
stop_words = set(stopwords.words("english"))
filtered = [w for w in tokens if w not in stop_words]

print("\nAFTER STOPWORD REMOVAL:")
print(filtered)

# Stemming
stemmer = PorterStemmer()
stemmed = [stemmer.stem(w) for w in filtered]

print("\nSTEMMED VERSION:")
print(stemmed)

# Lemmatization
lemmatizer = WordNetLemmatizer()
lemmatized = [lemmatizer.lemmatize(w) for w in filtered]

print("\nLEMMATIZED VERSION:")
print(lemmatized)
