import bcrypt

# Hash de referência usado quando o usuário não existe. Assim o tempo de resposta
# do login é parecido para usuário inexistente e senha errada, o que dificulta
# descobrir quais usernames estão cadastrados.
_HASH_FALSO = bcrypt.hashpw(b"senha-que-nao-existe", bcrypt.gensalt()).decode()


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str | None) -> bool:
    if hash_armazenado is None:
        hash_armazenado = _HASH_FALSO
        bcrypt.checkpw(senha.encode("utf-8")[:72], hash_armazenado.encode("utf-8"))
        return False

    try:
        # bcrypt só considera os 72 primeiros bytes da senha
        return bcrypt.checkpw(
            senha.encode("utf-8")[:72], hash_armazenado.encode("utf-8")
        )
    except ValueError:
        return False
