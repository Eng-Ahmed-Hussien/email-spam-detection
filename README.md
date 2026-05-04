# Email Spam Detection Using Machine Learning

A supervised machine learning system that classifies email and SMS messages as spam or legitimate (ham) using Natural Language Processing techniques. The project implements and compares three classification models: Naive Bayes, Support Vector Machine, and Neural Network, with a desktop graphical interface.

---

## Project Overview

Spam detection is a classical text classification problem that serves as a practical demonstration of NLP pipelines and supervised learning. This project covers the full pipeline from raw text preprocessing to model evaluation and deployment as a standalone desktop application.

---

## Requirements

### Core Tasks
- Text preprocessing using TF-IDF vectorization and stopword removal
- Training a Naive Bayes classifier
- Training a Support Vector Machine (SVM) classifier
- Training a Multilayer Perceptron (Neural Network) classifier
- Model evaluation using Accuracy, Precision, Recall, and F1-Score
- Confusion matrix generation for each model
- Visual comparison of model performance
- Deployment as a functional spam filter with a desktop GUI

### Evaluation Metrics
- Accuracy
- F1-Score
- Precision
- Recall
- Confusion Matrix

---

## Dataset

**SMS Spam Collection Dataset**
- Source: [Kaggle — SMS Spam Collection](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)
- Size: 5,572 messages (4,825 Ham / 747 Spam)
- Format: CSV with columns `v1` (label) and `v2` (text)
- After download, place `spam.csv` inside the `/data` directory

---

## Project Structure

```
email-spam-detection/
|-- data/
|   `-- spam.csv
|-- notebooks/
|   `-- spam_detection_EDA.ipynb
|-- src/
|   |-- __init__.py
|   |-- preprocess.py
|   |-- train.py
|   |-- evaluate.py
|   `-- predict.py
|-- models/
|   |-- vectorizer.pkl
|   |-- naive_bayes.pkl
|   |-- svm.pkl
|   `-- neural_network.pkl
|-- reports/
|   |-- cm_naive_bayes.png
|   |-- cm_svm.png
|   |-- cm_neural_network.png
|   `-- model_comparison.png
|-- app.py
|-- run.py
|-- build.bat
`-- requirements.txt
```

---

## Technology Stack

| Layer | Tool / Library |
|-------|----------------|
| Language | Python 3.10+ |
| NLP | NLTK, scikit-learn (TF-IDF) |
| ML Models | Naive Bayes, SVM, MLP Neural Network |
| Evaluation | scikit-learn metrics |
| Visualization | Matplotlib, Seaborn |
| GUI | CustomTkinter |
| Packaging | PyInstaller |
| Notebook | Jupyter |

---

## Setup and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/Eng-Ahmed-Hussien/email-spam-detection.git
cd email-spam-detection
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare the Dataset

Download `spam.csv` from the Kaggle link above and place it in the `/data` folder.

### 4. Train Models and Launch Application

```bash
python run.py
```

If models are already trained, launch the GUI directly:

```bash
python app.py
```

### 5. Run the Notebook (Exploratory Analysis)

```bash
python -m jupyter notebook notebooks/spam_detection_EDA.ipynb
```

---

## Build Executable (.exe)

```bash
build.bat
```

Output: `dist/SpamDetector.exe`

---

## Model Performance

| Model | Accuracy | F1-Score | Precision | Recall |
|-------|----------|----------|-----------|--------|
| Naive Bayes | ~97% | ~96% | ~97% | ~95% |
| SVM | ~98% | ~97% | ~99% | ~95% |
| Neural Network | ~98% | ~97% | ~98% | ~96% |

---

## Author

Ahmed Hussien
GitHub: [Eng-Ahmed-Hussien](https://github.com/Eng-Ahmed-Hussien)
Portfolio: [ahmedhussienportfolio-gamma.vercel.app](https://ahmedhussienportfolio-gamma.vercel.app)
