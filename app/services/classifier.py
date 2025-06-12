# app/services/classifier.py
from transformers import pipeline

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline(
            "audio-classification",
            model="pedromatias97/genre-recognizer-finetuned-gtzan_dset"
        )
    return _classifier

def classify(path: str) -> str:
    results = get_classifier()(path)
    return results[0]["label"]
