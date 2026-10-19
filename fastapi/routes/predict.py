from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from models.schemas import PredictRequest, PredictResponse
from models.database_models import User, Prediction
from database import get_session
from security.dependencies import get_current_user


predict_router = APIRouter()


@predict_router.post("/predict", response_model=PredictResponse)
def predict(
    data: PredictRequest,
    usuario: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    texto = data.message.lower()

    if "reembolso" in texto:
        intent = "refund"
    else:
        intent = "general_support"

    # A predição é salva com o owner_id do usuário autenticado
    prediction = Prediction(
        text=data.message,
        intent=intent,
        owner_id=usuario.id
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return {
        "id": prediction.id,
        "message": prediction.text,
        "intent": prediction.intent
    }


@predict_router.get("/predict/{prediction_id}")
def get_prediction(
    prediction_id: int,
    usuario: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Controle de acesso por ownership (BOLA): filtra pelo id E pelo dono.
    # Se a predição existe mas é de outro usuário, a resposta é a mesma de
    # "não existe" (404), sem revelar a existência do recurso.
    prediction = session.exec(
        select(Prediction).where(
            Prediction.id == prediction_id,
            Prediction.owner_id == usuario.id
        )
    ).first()

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="Prediction não encontrada"
        )

    return prediction
