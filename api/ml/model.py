from sklearn.linear_model import LinearRegression
from typing import List

def train_budget_model(X: List[List[float]], y: List[float]):
    model = LinearRegression()
    model.fit(X, y)
    return model