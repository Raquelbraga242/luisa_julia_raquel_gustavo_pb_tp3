from slowapi import Limiter
from slowapi.util import get_remote_address

# Limite do endpoint POST /auth/token: 10 requisições por minuto por cliente (IP).
# Justificativa: 10 tentativas por minuto atendem um usuário legítimo que erra a
# senha algumas vezes, mas reduzem muito a velocidade de um ataque de força bruta
# (no máximo 600 tentativas por hora por IP, contra milhares sem o limite).
LIMITE_AUTENTICACAO = "10/minute"

limiter = Limiter(key_func=get_remote_address)
