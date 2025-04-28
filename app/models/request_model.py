from pydantic import BaseModel
from typing import Any, Dict

class PredictRequest(BaseModel):
    # adjust fields to match the data your model will need
    input_data: Dict[str, Any]
