from celery import Celery
from app.config import settings


def celery_init_app() -> Celery:
    """
    Initialize and return a Celery application
    """
    c_app = Celery(
        "CELERY",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend

    )

    return c_app


celery_app = celery_init_app()

# import os
# from celery import Celery, Task
# from fastapi import FastAPI


# def celery_init_app(app: FastAPI) -> Celery:
#     class FastAPITask(Task):
#         """
#         Custom task class to integrate FastAPI app context into Celery Tasks
#         """

#         def __call__(self, *args: object, **kwargs: object) -> object:
#             with app.state.app_context():
#                 return self.run(*args, **kwargs)

#     celery_app = None
#     # print(f"------{os.name}-------->")
#     if os.name == "posix":
#         celery_app = Celery(app.title, task_cls=FastAPITask)
#         celery_app.config_from_object(app.state.config["CELERY"])
#         celery_app.set_default()
#     else:
#         celery_app = Celery(app.title)
#         celery_app.config_from_object(app.state.config["CELERY"])
#         celery_app.set_default()
#         celery_app.Task = FastAPITask

#     app.state.celery = celery_app

#     return celery_app
