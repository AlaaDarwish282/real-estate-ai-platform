import pandas as pd
import numpy as np
from datetime import datetime


class MarketAnalyzer:
    """
    Real estate market analytics: price trends, neighborhood scoring,
    investment opportunity scoring, and comparative market analysis (CMA).
    """

    def price_trend(self, df: pd.DataFrame, date_col: str = "sale_date",
                    price_col: str = "sale_price", freq: str = "M") -> pd.DataFrame:
        """Compute median price trend over time."""
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
        trend = df[price_col].resample(freq).agg(["median", "mean", "count"])
        trend["pct_change"] = trend["median"].pct_change() * 100
        trend.columns = ["median_price", "avg_price", "num_sales", "mom_change_pct"]
        return trend.reset_index()

    def neighborhood_score(self, neighborhood: dict) -> dict:
        """
        Compute a composite neighborhood score (0-100) based on:
        school quality, safety, walkability, amenities, price appreciation.
        """
        weights = {
            "school_rating": 0.25,
            "safety_score": 0.25,
            "walkability": 0.20,
            "amenities_score": 0.15,
            "appreciation_rate": 0.15,
        }
        score = 0.0
        breakdown = {}
        for key, weight in weights.items():
            val = neighborhood.get(key, 50)
            normalized = max(0, min(100, val))
            breakdown[key] = round(normalized * weight, 2)
            score += normalized * weight

        return {
            "composite_score": round(score, 1),
            "grade": "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D",
            "breakdown": breakdown,
        }

    def investment_score(self, property: dict, market: dict) -> dict:
        """
        Score a property's investment potential (0-100).
        Considers cap rate, price appreciation, rental yield, liquidity.
        """
        price = property.get("price", 1)
        annual_rent = property.get("annual_rent_estimate", 0)
        annual_expenses = property.get("annual_expenses", annual_rent * 0.35)
        noi = annual_rent - annual_expenses
        cap_rate = (noi / price) * 100 if price > 0 else 0

        appreciation = market.get("annual_appreciation_pct", 3.0)
        days_on_market = property.get("days_on_market", 60)
        liquidity_score = max(0, 100 - days_on_market)

        score = (
            min(cap_rate * 10, 40) +      # up to 40 pts for cap rate
            min(appreciation * 5, 30) +   # up to 30 pts for appreciation
            liquidity_score * 0.3          # up to 30 pts for liquidity
        )

        return {
            "investment_score": round(min(score, 100), 1),
            "cap_rate_pct": round(cap_rate, 2),
            "annual_noi": round(noi, 2),
            "gross_yield_pct": round((annual_rent / price) * 100, 2),
            "recommendation": "Strong Buy" if score >= 75 else
                              "Buy" if score >= 55 else
                              "Hold" if score >= 40 else "Avoid",
        }

    def cma(self, subject: dict, comps: list[dict]) -> dict:
        """Comparative Market Analysis against similar sold properties."""
        prices = [c.get("sale_price", 0) for c in comps if c.get("sale_price")]
        psf = [c.get("sale_price", 0) / c.get("area_sqft", 1) for c in comps]
        return {
            "subject_property": subject,
            "num_comps": len(comps),
            "median_comp_price": round(float(np.median(prices)), 2) if prices else None,
            "avg_price_per_sqft": round(float(np.mean(psf)), 2) if psf else None,
            "estimated_value": round(float(np.median(psf)) * subject.get("area_sqft", 1), 2) if psf else None,
            "price_range": {"low": round(min(prices), 2), "high": round(max(prices), 2)} if prices else None,
        }
