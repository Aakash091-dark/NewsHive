from pydantic import BaseModel

class SummaryResponse(BaseModel):
    summary: str

class TaxonomyClassificationResponse(BaseModel):
    category: str
    subcategory: str