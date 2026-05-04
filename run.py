"""Quick launcher - trains models if not found, then opens the app."""
import os
import subprocess
import sys

def main():
    models_ready = all(os.path.exists(p) for p in [
        'models/vectorizer.pkl', 'models/svm.pkl'
    ])

    if not models_ready:
        print("Models not found. Training now...")
        from src.train import train_all
        train_all()

    from app import SpamDetectorApp
    SpamDetectorApp().mainloop()

if __name__ == '__main__':
    main()
