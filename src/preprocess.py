import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

nltk.download('stopwords', quiet=True)

STEMMER = PorterStemmer()
STOP_WORDS = set(stopwords.words('english'))


def clean_text(text: str) -> str:
    """Lowercase, remove special chars, remove stopwords, stem."""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS]
    return ' '.join(tokens)


def load_and_preprocess(data_path: str = 'data/spam.csv'):
    """
    Load dataset, clean text, vectorize with TF-IDF.
    Returns: X_train, X_test, y_train, y_test, vectorizer
    """
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(data_path, encoding='latin-1')[['v1', 'v2']]
    df.columns = ['label', 'text']
    df['label'] = df['label'].map({'ham': 0, 'spam': 1})
    df['clean_text'] = df['text'].apply(clean_text)

    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['label'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Save vectorizer
    os.makedirs('models', exist_ok=True)
    with open('models/vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

    return X_train, X_test, y_train, y_test, vectorizer
