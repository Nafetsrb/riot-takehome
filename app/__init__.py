"""App package initializer.

The application follows an architecture design:
- Strategy pattern for crypto & signature (app/crypto/* and app/signature/*)
- Dependency Injection via FastAPI Depends (app/deps.py)
- Configuration via Pydantic Settings (app/config.py)
- Cross-cutting concerns as middleware (request ID, body limit) & exception handlers.
"""
__all__: list[str] = []
