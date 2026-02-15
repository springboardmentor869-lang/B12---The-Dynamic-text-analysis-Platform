import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

class TextCleaner:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def clean(self, text):
        # 1. Remove symbols & numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
        # 2. Tokenize
        tokens = word_tokenize(text)
        # 3. Remove Stopwords
        filtered = [w for w in tokens if w not in self.stop_words]
        
        # 4. Create Stemmed and Lemmatized versions
        stemmed = [self.stemmer.stem(w) for w in filtered]
        lemmed = [self.lemmatizer.lemmatize(w) for w in filtered]
        
        return " ".join(stemmed), " ".join(lemmed)