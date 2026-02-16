from datetime import datetime
from typing import List

def build_features(
    X_days: List[List[float]],
    budget_start: datetime,
    budget_end: datetime
) -> List[List[float]]:

    total_days = (budget_end - budget_start).days + 1
    features = []

    for [day] in X_days:
        progress_ratio = day / total_days
        features.append([day, progress_ratio])

    return features