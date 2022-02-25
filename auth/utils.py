import secrets
from time import time
from auth.schemas import ApplicationLogin
from auth.models import Application
import core.service as service
import hashlib


async def get_data():
    app_id = secrets.token_hex(20)
    app_secret = secrets.token_hex(64)
    return app_id, app_secret


async def check_app(app: ApplicationLogin, params):
    detail_service = service.DetailMixin(query_value=["app_id", app.app_id], db=params['db'], model=Application)
    app_db: Application = await detail_service.get_detail()
    return True if app_db and hashlib.sha256(str(app.app_secret).encode("utf-8")).hexdigest() == app_db.app_secret else False
