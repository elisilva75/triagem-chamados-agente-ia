from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from app.agent.simulated import SimulatedProvider
from app.api.routes import router
from app.api.schemas import ErrorResponse
from app.config import Settings
from app.domain.editing import TicketError
from app.infrastructure.database import make_engine, make_sessions


def error(request: Request, status: int, code: str, message: str, details=None):
    return JSONResponse(
        status_code=status,
        headers={"X-Request-ID": request.state.request_id},
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
                "request_id": request.state.request_id,
            }
        },
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = make_engine(settings.database_url.get_secret_value())

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    app = FastAPI(
        title="Triagem de Chamados — uso local sem autenticação",
        version="0.3.0",
        description="Cadastro, consulta, edição e triagem exclusivamente simulada. Uso local.",
        lifespan=lifespan,
        responses={code: {"model": ErrorResponse} for code in (404, 409, 422, 500, 502, 503, 504)},
    )
    app.state.sessions = make_sessions(engine)
    app.state.engine = engine
    app.state.provider = SimulatedProvider()

    @app.exception_handler(TicketError)
    async def ticket_error(request, exc):
        return error(request, exc.status, exc.code, exc.message, getattr(exc, "details", None))

    @app.middleware("http")
    async def request_id(request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        details = [
            {"field": ".".join(map(str, item["loc"])), "code": item["type"]}
            for item in exc.errors()
        ]
        return error(request, 422, "validation_error", "Entrada inválida.", details)

    @app.exception_handler(SQLAlchemyError)
    async def storage_error(request, exc):
        return error(request, 503, "storage_unavailable", "Persistência indisponível.")

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        code = "not_found" if exc.status_code == 404 else "http_error"
        return error(request, exc.status_code, code, "Recurso ou operação indisponível.")

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        return error(request, 500, "internal_error", "Erro interno.")

    app.include_router(router)
    return app
