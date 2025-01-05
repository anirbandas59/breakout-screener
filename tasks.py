import uvicorn
from app.main import create_app
from app.config import settings

app = create_app()


if __name__ == '__main__':
    uvicorn.run(app, host=settings.app_hostname, port=settings.app_port)
