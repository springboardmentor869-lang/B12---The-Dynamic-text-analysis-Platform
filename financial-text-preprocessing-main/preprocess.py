import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Sample financial text (you can replace this with your document text later)
text = """
The company's revenue increased by 25% in 2023.
However, operational costs also rose significantly.
This financial performance indicates strong growth.
"""

# 1️⃣ CLEANING (remove numbers and special characters)
cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
cleaned_text = cleaned_text.lower()

print("Cleaned Text:\n", cleaned_text)

# 2️⃣ TOKENIZATION
tokens = word_tokenize(cleaned_text)
print("\nTokens:\n", tokens)

# 3️⃣ REMOVE STOPWORDS
stop_words = set(stopwords.words('english'))
filtered_tokens = [word for word in tokens if word not in stop_words]

print("\nAfter Stopword Removal:\n", filtered_tokens)

# 4️⃣ STEMMING
stemmer = PorterStemmer()
stemmed_words = [stemmer.stem(word) for word in filtered_tokens]

print("\nStemmed Version:\n", stemmed_words)

# 5️⃣ LEMMATIZATION
lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_tokens]

print("\nLemmatized Version:\n", lemmatized_words)