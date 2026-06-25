from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from ml.price_predictor import PropertyPricePredictor
from ml.recommendation import PropertyRecommender
from analytics.market_analysis import MarketAnalyzer

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])
predictor = PropertyPricePredictor()
analyzer = MarketAnalyzer()


class PropertyFeatures(BaseModel):
    area_sqft: float
    bedrooms: int
    bathrooms: float
    year_built: int
    distance_to_center_km: float
    school_rating: float = 7.0
    crime_index: float = 30.0
    garage: int = 1
    pool: int = 0
    lot_size_sqft: float = 5000.0


class ValuationResponse(BaseModel):
    predicted_price: float
    confidence: float
    price_range_low: float
    price_range_high: float


@router.post("/valuate", response_model=ValuationResponse)
def valuate_property(features: PropertyFeatures):
    """AI-powered property valuation."""
    try:
        result = predictor.predict(features.model_dump())
        return result
    except RuntimeError:
        # Return demo estimate if model not trained
        base = features.area_sqft * 180
        return {"predicted_price": base, "confidence": 0.70,
                "price_range_low": base * 0.92, "price_range_high": base * 1.08}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NeighborhoodRequest(BaseModel):
    school_rating: float = 75.0
    safety_score: float = 70.0
    walkability: float = 65.0
    amenities_score: float = 80.0
    appreciation_rate: float = 5.0


@router.post("/neighborhood-score")
def neighborhood_score(req: NeighborhoodRequest):
    return analyzer.neighborhood_score(req.model_dump())


class InvestmentRequest(BaseModel):
    price: float
    annual_rent_estimate: float
    annual_expenses: Optional[float] = None
    days_on_market: int = 45
    area: dict = {}


@router.post("/investment-score")
def investment_score(req: InvestmentRequest):
    market = {"annual_appreciation_pct": req.area.get("appreciation_pct", 4.0)}
    return analyzer.investment_score(req.model_dump(), market)
