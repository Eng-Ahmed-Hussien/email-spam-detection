import pickle
from src.preprocess import clean_text


def load_model(model_name: str = 'svm'):
    with open(f'models/{model_name}.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('models/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer


def predict(text: str, model_name: str = 'svm') -> dict:
    """
    Predict whether a message is Spam or Ham.
    All 3 models now support predict_proba, so confidence is always real.
    Returns: { 'label': 'Spam'|'Ham', 'confidence': float, 'spam_prob': float, 'ham_prob': float }
    """
    model, vectorizer = load_model(model_name)
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])

    prediction = model.predict(X)[0]
    proba      = model.predict_proba(X)[0]   # [ham_prob, spam_prob]

    ham_prob  = round(proba[0] * 100, 2)
    spam_prob = round(proba[1] * 100, 2)
    confidence = round(max(proba) * 100, 2)

    return {
        'label':      'Spam' if prediction == 1 else 'Ham',
        'confidence': confidence,
        'spam_prob':  spam_prob,
        'ham_prob':   ham_prob,
    }
