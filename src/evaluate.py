import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score,
    recall_score, confusion_matrix, classification_report
)
import os


def evaluate_model(model, X_test, y_test, model_name: str) -> dict:
    """Evaluate a model and save confusion matrix plot."""
    y_pred = model.predict(X_test)

    metrics = {
        'accuracy':  accuracy_score(y_test, y_pred),
        'f1':        f1_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall':    recall_score(y_test, y_pred),
    }

    print(f"\n--- {model_name.upper()} ---")
    print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))

    _plot_confusion_matrix(y_test, y_pred, model_name)
    return metrics


def _plot_confusion_matrix(y_test, y_pred, model_name: str):
    os.makedirs('reports', exist_ok=True)
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=['Ham', 'Spam'],
        yticklabels=['Ham', 'Spam'],
        ax=ax
    )
    ax.set_title(f'Confusion Matrix - {model_name.replace("_", " ").title()}')
    ax.set_ylabel('Actual')
    ax.set_xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(f'reports/cm_{model_name}.png', dpi=150)
    plt.close()


def plot_model_comparison(results: dict):
    """Bar chart comparing Accuracy and F1 across all models."""
    os.makedirs('reports', exist_ok=True)
    names = [n.replace('_', ' ').title() for n in results.keys()]
    accuracies = [v['accuracy'] for v in results.values()]
    f1_scores  = [v['f1']       for v in results.values()]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, accuracies, width, label='Accuracy', color='#2196F3')
    ax.bar(x + width / 2, f1_scores,  width, label='F1-Score',  color='#4CAF50')

    ax.set_ylim(0.9, 1.0)
    ax.set_ylabel('Score')
    ax.set_title('Model Performance Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    plt.tight_layout()
    plt.savefig('reports/model_comparison.png', dpi=150)
    plt.close()
    print("Comparison chart saved to reports/model_comparison.png")
