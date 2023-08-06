import os
from pyramid.config import Configurator
from pyramid.view import view_config

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    for var in ('EWS_DOMAIN', 'EWS_USER', 'EWS_PASS'):
        settings[var.lower()] = os.getenv(var)
    config = Configurator(settings=settings)
    config.include(includeme)
    config.add_route('ewscal', '/')
    config.scan()
    return config.make_wsgi_app()

def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('freebusy', '/freebusy')
    config.scan('ewscal.freebusy')
    
@view_config(route_name='ewscal', renderer="templates/index.pt")
def index(request):
    """Just a help page; the action is at static/index.html"""
    return {}
