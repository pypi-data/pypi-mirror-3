from os import path
from beaker.middleware import SessionMiddleware
from paste.registry import RegistryManager
from blazeweb import config, settings
from blazeweb.application import WSGIApp
from basebwa.middleware import ElixirApp
from blazeweb import routing
from werkzeug import SharedDataMiddleware, DebuggedApplication
import settings as settingsmod

def make_wsgi(profile='Default'):

    config.appinit(settingsmod, profile)

    app = WSGIApp()

    app = ElixirApp(app)

    app = SessionMiddleware(app, **dict(settings.beaker))

    app = RegistryManager(app)

    # serve static files from main app and supporting apps (need to reverse order b/c
    # middleware stack is run in bottom up order).  This works b/c if a
    # static file isn't found, the ShardDataMiddleware just forwards the request
    # to the next app.
    for appname in config.appslist(reverse=True):
        app_py_mod = __import__(appname)
        fs_static_path = path.join(path.dirname(app_py_mod.__file__), 'static')
        static_map = {routing.add_prefix('/') : fs_static_path}
        app = SharedDataMiddleware(app, static_map)

    # show nice stack traces and debug output if enabled
    if settings.debugger.enabled:
        app = DebuggedApplication(app, evalex=settings.debugger.interactive)

    return app
