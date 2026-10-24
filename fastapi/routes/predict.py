from database import get_session
from models.database_models import Prediction, User
from models.schemas import PredictRequest, PredictResponse
from security.dependencies import get_current_user
from sqlmodel import Session, select

from fastapi import APIRouter, Depends, HTTPException

predict_router = APIRouter(tags=["Predição"])


@predict_router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Classifica a intenção de uma mensagem de suporte",
    responses={
        200: {"description": "Intenção classificada e registrada com sucesso"},
        401: {"description": "Token JWT ausente, inválido ou expirado"},
    },
)
def predict(
    data: PredictRequest,
    usuario: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Recebe o texto de um chamado, classifica a intenção e salva o registro
    vinculado ao usuário autenticado. Requer autenticação Bearer Token (JWT).
    """
    texto = data.message.lower()

    if "reembolso" in texto:
        intent = "refund"
    else:
        intent = "general_support"

    # A predição é salva com o owner_id do usuário autenticado
    prediction = Prediction(text=data.message, intent=intent, owner_id=usuario.id)
    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return {
        "id": prediction.id,
        "message": prediction.text,
        "intent": prediction.intent,
    }


@predict_router.get(
    "/predict/{prediction_id}",
    summary="Consulta uma predição pelo ID",
    responses={
        200: {"description": "Predição encontrada e retornada com sucesso"},
        401: {"description": "Token JWT ausente, inválido ou expirado"},
        404: {"description": "Predição não encontrada ou pertencente a outro usuário"},
    },
)
def get_prediction(
    prediction_id: int,
    usuario: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Busca uma predição específica pelo `prediction_id`.
    Requer autenticação via Bearer Token (JWT).
    """

    # Controle de acesso por ownership (BOLA): filtra pelo id E pelo dono.
    # Se a predição existe mas é de outro usuário, a resposta é a mesma de
    # "não existe" (404), sem revelar a existência do recurso.
    prediction = session.exec(
        select(Prediction).where(
            Prediction.id == prediction_id, Prediction.owner_id == usuario.id
        )
    ).first()

    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction não encontrada")

    return prediction
