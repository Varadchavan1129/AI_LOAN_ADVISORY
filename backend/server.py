"""
Entrypoint for the Emergent-hosted environment.

Supervisor runs `uvicorn server:app --host 0.0.0.0 --port 8001`.
The full application lives in app/main.py. All routes there are served
under the `/api` prefix so they route correctly through the Kubernetes ingress.
"""
from app.main import app  # noqa: F401
