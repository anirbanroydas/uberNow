from tornado import web
from tornado.web import URLSpec as url
from sockjs.tornado import SockJSRouter

from settings import settings
from utils import include
from apps.main.views import UbernowRequestHandler


# Register SocjJsRouter Connection
SockjsWebsocketRouter = SockJSRouter(UbernowRequestHandler, '/ubernow')

urls = [
    url(r"/static/(.*)", web.StaticFileHandler,
        {"path": settings.get('static_path')}),
]
urls += include(r"/", "apps.main.urls")

urls = urls + SockjsWebsocketRouter.urls


