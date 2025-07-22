# backend/models.py
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ReceiptData(BaseModel):
    vendor: str = Field(..., min_length=2, max_length=50)
    date: str
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=2)

    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            try:
                datetime.strptime(v, "%d/%m/%Y")
            except ValueError:
                raise ValueError("Date must be in DD-MM-YYYY or DD/MM/YYYY format")
        return v
