"""
Dependency injection for Celery task management.

Provides a CeleryTaskDispatcher that can be injected into route handlers,
isolating the celery_app import to a single module and enabling easy mocking in tests.
"""
from typing import Optional
from celery import Celery
from celery.result import AsyncResult

from app.celery import celery_app


class CeleryTaskDispatcher:
    """
    Wraps Celery task result querying and worker inspection.

    Inject via FastAPI Depends(get_celery_dispatcher) instead of importing
    celery_app directly in route handlers.

    In tests, override with:
        app.dependency_overrides[get_celery_dispatcher] = lambda: MockDispatcher()
    """

    def __init__(self, app: Celery):
        self._app = app

    def get_task_result(self, task_id: str) -> AsyncResult:
        """Return an AsyncResult for the given task_id."""
        return AsyncResult(task_id, app=self._app)

    def inspect_active(self) -> Optional[dict]:
        """Return active tasks from all workers, or None if unavailable."""
        return self._app.control.inspect().active()


def get_celery_dispatcher() -> CeleryTaskDispatcher:
    """FastAPI dependency that provides a CeleryTaskDispatcher instance."""
    return CeleryTaskDispatcher(celery_app)
