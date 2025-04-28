# app/routers/predict.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Union
from app.services.prediction import predict

class PredictRequest(BaseModel):
    input_data: Dict[
        str,
        Union[int, str]
    ] = Field(
        ...,
        description="Keys: Source Port (int), Destination Port (int), Protocol (str), "
                    "Packet Length (int), Packet Type (str), Traffic Type (str)"
    )

router = APIRouter()

@router.post("/predict")
async def make_prediction(req: PredictRequest):
    try:
        attack = predict(req.input_data)
        return {"attack_type": attack}
    except HTTPException as e:
        # propagate 400/500 as declared
        raise e
    except Exception as e:
        # catch-all fallback
        raise HTTPException(status_code=500, detail=str(e))
