from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.database_models import User
from security.jwt import validar_token_jwt


def get_current_user(
    username: str = Depends(validar_token_jwt),
    session: Session = Depends(get_session)
) -> User:
    """Devolve o usuário dono do token JWT.

    Rejeita com 401 tokens válidos de usuários que não existem mais no banco.
    """
    usuario = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return usuario
