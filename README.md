# 📧 Email Spam Detection

> AI Project — Email Spam Detection using NLP & Machine Learning

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python) ![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange) ![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green) ![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

---

## 📌 Project Overview

Build a Machine Learning model that classifies emails as **Spam** or **Not Spam (Ham)** using Natural Language Processing (NLP) techniques and supervised learning algorithms. The project includes a desktop GUI application exported as `.exe`.

---

## 🎯 Requirements (As per Doctor's Specification)

### ✅ Core Tasks
- [ ] Preprocess text data (TF-IDF, stopwords removal, tokenization)
- [ ] Train **Naïve Bayes** classifier
- [ ] Train **SVM** classifier
- [ ] Train **Neural Network** classifier
- [ ] Compare models using Accuracy and F1-Score metrics
- [ ] Deploy as a functional spam filter with performance analysis

### ✅ Evaluation Metrics
- Accuracy
- F1-Score
- Precision & Recall
- Confusion Matrix

### ✅ Expected Outcome
- Deployed spam filter with full performance analysis
- Visual comparison between all 3 models
- Desktop GUI App (.exe)

---

## 📂 Project Structure

```
email-spam-detection/
├── data/
│   └── spam.csv                  # Dataset (SMS Spam Collection)
├── notebooks/
│   └── exploration.ipynb         # EDA & experimentation
├── src/
│   ├── preprocess.py             # Text cleaning & TF-IDF vectorization
│   ├── train.py                  # Train all 3 models
│   ├── evaluate.py               # Metrics & confusion matrix
│   └── predict.py                # Prediction function for GUI
├── models/
│   ├── naive_bayes.pkl
│   ├── svm.pkl
│   └── neural_net.pkl
├── app.py                        # GUI (CustomTkinter)
├── requirements.txt
├── README.md
└── dist/
    └── SpamDetector.exe          # Final executable
```

---

## 🗂️ Dataset

**SMS Spam Collection Dataset**
- 📦 Source: [Kaggle - SMS Spam Collection](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)
- 📊 Size: 5,572 messages (4,825 Ham + 747 Spam)
- 📁 Format: CSV with columns `label` (spam/ham) and `text`
- ✅ Clean, labeled, ready to use — perfect for this project

> Download and place `spam.csv` inside the `/data` folder.

---

## ⚙️ Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| NLP | NLTK, scikit-learn (TF-IDF) |
| ML Models | Naïve Bayes, SVM, MLP Neural Network |
| Visualization | Matplotlib, Seaborn |
| GUI | CustomTkinter |
| Packaging | PyInstaller (.exe) |
| Notebook | Jupyter |

---

## 🚀 Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/Eng-Ahmed-Hussien/email-spam-detection.git
cd email-spam-detection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download dataset and place in /data
# https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset

# 4. Train the models
python src/train.py

# 5. Run the GUI app
python app.py
```

---

## 🖥️ Build .exe

```bash
pyinstaller --onefile --windowed app.py
# Output: dist/SpamDetector.exe
```

---

## 📊 Model Comparison (Expected)

| Model | Accuracy | F1-Score |
|-------|----------|----------|
| Naïve Bayes | ~97% | ~96% |
| SVM | ~98% | ~97% |
| Neural Network | ~98% | ~97% |

---

## 👨‍💻 Developer

**Ahmed Hussien** — [GitHub](https://github.com/Eng-Ahmed-Hussien) | [Portfolio](https://ahmedhussienportfolio-gamma.vercel.app)
