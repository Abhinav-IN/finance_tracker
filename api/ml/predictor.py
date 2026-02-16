import joblib

_model = None


def load_model():
    global _model
    if _model is None:
        _model = joblib.load("api/ml/models/daily_spend_model.pkl")
    return _model


def predict_daily_spend(features: list[float]) -> float:
    """
    Predicts DAILY spend.
    features example:
    [avg_daily_spend_so_far]
    """
    model = load_model()
    prediction = model.predict([features])[0]
    return max(prediction, 0)