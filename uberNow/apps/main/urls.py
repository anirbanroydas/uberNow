from tornado.web import URLSpec as url
from uberNow.apps.main.views import IndexHandler

urls = [
    url(r"/", IndexHandler),
]
