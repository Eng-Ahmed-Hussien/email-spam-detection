"""
Launcher:
  - Checks if trained models exist.
  - If not, runs training as a SEPARATE subprocess (avoids tkinter thread conflict).
  - Then launches the GUI in the main thread.
"""
import os
import sys
import subprocess

MODEL_FILES = [
    'models/vectorizer.pkl',
    'models/naive_bayes.pkl',
    'models/svm.pkl',
    'models/neural_network.pkl',
]


def models_ready() -> bool:
    return all(os.path.exists(p) for p in MODEL_FILES)


def run_training():
    """Train in a completely separate Python process to avoid tkinter conflicts."""
    print("Models not found. Starting training...")
    result = subprocess.run(
        [sys.executable, '-m', 'src.train'],
        check=True
    )
    if result.returncode != 0:
        print("Training failed. Exiting.")
        sys.exit(1)
    print("Training complete.")


def launch_app():
    """Import and launch the GUI only after training is done."""
    from app import SpamDetectorApp
    app = SpamDetectorApp()
    app.mainloop()


if __name__ == '__main__':
    if not models_ready():
        run_training()
    launch_app()
