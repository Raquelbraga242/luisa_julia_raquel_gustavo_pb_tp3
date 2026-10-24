from fastapi import APIRouter

health_router = APIRouter(tags=["Monitoramento"])


@health_router.get(
    "/health",
    summary="Verifica a disponibilidade da API",
    responses={200: {"description": "API em execução normal"}},
)
async def health():
    """
    Endpoint público de healthcheck para confirmar que o serviço está ativo.
    """
    return {"status": "ok"}
