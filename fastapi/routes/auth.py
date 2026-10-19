from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from database import get_session
from models.database_models import User
from security.jwt import gerar_token
from security.passwords import verificar_senha
from security.rate_limit import LIMITE_AUTENTICACAO, limiter


router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/token")
@limiter.limit(LIMITE_AUTENTICACAO)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    usuario = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    senha_correta = verificar_senha(
        form_data.password,
        usuario.password if usuario else None
    )

    # Mesma mensagem para usuário inexistente e senha errada, para não revelar
    # quais usernames existem.
    if not usuario or not senha_correta:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    token = gerar_token(usuario.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
