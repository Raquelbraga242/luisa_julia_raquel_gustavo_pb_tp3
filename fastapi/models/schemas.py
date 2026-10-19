from pydantic import BaseModel, ConfigDict


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class PredictResponse(BaseModel):
    id: int
    message: str
    intent: str

