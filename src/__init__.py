"""
src package — Spam Email Detector
===================================
Public API:
    from src.preprocess import load_and_preprocess, clean_text
    from src.train      import train_all
    from src.evaluate   import evaluate_model, plot_model_comparison
    from src.predict    import predict
"""

from src.preprocess import load_and_preprocess, clean_text
from src.predict    import predict

__all__ = [
    "load_and_preprocess",
    "clean_text",
    "predict",
]
