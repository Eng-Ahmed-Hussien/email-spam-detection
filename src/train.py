import pickle
import os
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from src.preprocess import load_and_preprocess
from src.evaluate import evaluate_model, plot_model_comparison


def train_all(data_path: str = 'data/spam.csv') -> dict:
    print("Loading and preprocessing data...")
    X_train, X_test, y_train, y_test, _ = load_and_preprocess(data_path)

    models = {
        # alpha=0.1 gives better recall on spam vs default alpha=1.0
        'naive_bayes': MultinomialNB(alpha=0.1),

        # SVC with probability=True gives real confidence scores (no hardcoded fallback)
        'svm': SVC(kernel='linear', probability=True, C=1.0, random_state=42),

        'neural_network': MLPClassifier(
            hidden_layer_sizes=(128, 64),
            max_iter=50,
            random_state=42
        ),
    }

    results = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)

        os.makedirs('models', exist_ok=True)
        with open(f'models/{name}.pkl', 'wb') as f:
            pickle.dump(model, f)

        metrics = evaluate_model(model, X_test, y_test, name)
        results[name] = metrics
        print(f"  Accuracy: {metrics['accuracy']:.4f} | F1: {metrics['f1']:.4f}")

    plot_model_comparison(results)
    print("\nAll models trained and saved to /models")
    return results


if __name__ == '__main__':
    train_all()
