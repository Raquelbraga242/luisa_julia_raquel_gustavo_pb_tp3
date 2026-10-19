from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from routes.auth import router as auth_router
from routes.health import health_router
from routes.predict import predict_router
from security.cors import CONFIG_CORS
from security.headers import adicionar_headers_seguranca
from security.rate_limit import limiter


app = FastAPI(
    title="Customer Support API"
)

# Rate limiting (SlowAPI): o limiter precisa estar em app.state e o handler
# transforma RateLimitExceeded em resposta HTTP 429.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Headers de segurança HTTP em todas as respostas (HSTS, X-Frame-Options,
# X-Content-Type-Options e Content-Security-Policy).
app.middleware("http")(adicionar_headers_seguranca)

# CORS com allowlist explícita de origens. Adicionado por último para ficar como
# middleware mais externo e responder corretamente ao preflight (OPTIONS).
app.add_middleware(CORSMiddleware, **CONFIG_CORS)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(predict_router)
