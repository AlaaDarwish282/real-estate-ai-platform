import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import math


class PropertyPricePredictor:
    """
    Gradient Boosting model for residential property price prediction.
    Features: location, size, age, amenities, market conditions.
    """

    FEATURE_COLS = [
        "area_sqft", "bedrooms", "bathrooms", "floors", "garage",
        "pool", "year_built", "lot_size_sqft", "distance_to_center_km",
        "school_rating", "crime_index", "median_income_area",
        "price_per_sqft_neighborhood", "days_on_market_avg",
    ]

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=400, max_depth=5, learning_rate=0.05,
            subsample=0.8, random_state=42,
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["age"] = 2024 - df.get("year_built", 2000)
        df["price_per_sqft"] = df.get("list_price", 0) / (df["area_sqft"] + 1)
        df["bed_bath_ratio"] = df["bedrooms"] / (df["bathrooms"] + 1)
        df["total_rooms"] = df["bedrooms"] + df["bathrooms"]
        return df

    def train(self, df: pd.DataFrame, target_col: str = "sale_price") -> dict:
        df = self._engineer_features(df)
        available = [c for c in self.FEATURE_COLS if c in df.columns]
        X = df[available].fillna(df[available].median())
        y = df[target_col]

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

        preds = self.model.predict(X_scaled)
        mae = mean_absolute_error(y, preds)
        r2 = r2_score(y, preds)

        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, scoring="r2")

        importance = dict(zip(available, self.model.feature_importances_.tolist()))
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "mae": round(mae, 2),
            "r2_score": round(r2, 4),
            "cv_r2_mean": round(float(cv_scores.mean()), 4),
            "cv_r2_std": round(float(cv_scores.std()), 4),
            "top_features": dict(top_features),
            "training_samples": len(df),
        }

    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call .train() first.")
        df = pd.DataFrame([features])
        df = self._engineer_features(df)
        available = [c for c in self.FEATURE_COLS if c in df.columns]
        X = df[available].fillna(0)
        X_scaled = self.scaler.transform(X)
        price = float(self.model.predict(X_scaled)[0])
        confidence = min(0.95, max(0.50, 0.95 - abs(price - 300000) / 2_000_000))
        return {
            "predicted_price": round(price, 2),
            "confidence": round(confidence, 2),
            "price_range_low": round(price * 0.92, 2),
            "price_range_high": round(price * 1.08, 2),
        }

    def save(self, path: str) -> None:
        joblib.dump({"model": self.model, "scaler": self.scaler}, path)

    def load(self, path: str) -> None:
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.is_trained = True
