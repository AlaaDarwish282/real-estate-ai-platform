import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


class PropertyRecommender:
    """
    Content-based property recommender using cosine similarity
    on normalized property feature vectors.
    """

    FEATURE_COLS = [
        "price", "area_sqft", "bedrooms", "bathrooms",
        "distance_to_center_km", "school_rating", "crime_index",
    ]

    def __init__(self):
        self.scaler = MinMaxScaler()
        self.properties_df: pd.DataFrame = None
        self.feature_matrix: np.ndarray = None

    def fit(self, properties: pd.DataFrame) -> None:
        """Index a catalog of properties for similarity search."""
        self.properties_df = properties.reset_index(drop=True)
        available = [c for c in self.FEATURE_COLS if c in properties.columns]
        X = properties[available].fillna(properties[available].median())
        self.feature_matrix = self.scaler.fit_transform(X)

    def recommend(self, preferences: dict, top_k: int = 5,
                  max_price: float = None) -> list[dict]:
        """Return top-k properties matching user preferences."""
        if self.properties_df is None:
            raise RuntimeError("Call .fit() first.")

        available = [c for c in self.FEATURE_COLS if c in self.properties_df.columns]
        query = np.array([[preferences.get(c, 0) for c in available]])
        query_scaled = self.scaler.transform(query)

        sims = cosine_similarity(query_scaled, self.feature_matrix)[0]
        indices = np.argsort(sims)[::-1]

        results = []
        for idx in indices:
            row = self.properties_df.iloc[idx].to_dict()
            if max_price and row.get("price", 0) > max_price:
                continue
            row["similarity_score"] = round(float(sims[idx]), 4)
            results.append(row)
            if len(results) >= top_k:
                break

        return results
