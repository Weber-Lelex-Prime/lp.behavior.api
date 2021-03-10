from fastapi import FastAPI

#from app.api.errors.http_error import http_error_handler
#from app.api.errors.validation_error import http422_error_handler
from app.services.lambdaServices import lambdaService
from app.api.routes.api import router as api_router
#from app.core.config import ALLOWED_HOSTS, API_PREFIX, DEBUG, PROJECT_NAME, VERSION#
#from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    application = FastAPI()

    application.include_router(api_router)

    lambdaServiceManager = lambdaService()

    return application


app = get_application()