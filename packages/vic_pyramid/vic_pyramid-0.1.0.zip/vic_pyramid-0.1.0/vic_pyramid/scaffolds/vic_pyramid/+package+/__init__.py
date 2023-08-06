from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings

from .models import setup_database
from .request import WebRequest

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # setup database
    settings = setup_database(global_config, **settings)
    # make a session factory
    session_factory = session_factory_from_settings(settings)
    # create Pyramid configuration
    config = Configurator(
        settings=settings,
        request_factory=WebRequest,
        session_factory=session_factory
    )
    # add Genshi renderer
    config.include('pyramid_genshi')
    # map URLs
    config.include('.url_map.map_urls')
    # scan modules
    config.scan()
    return config.make_wsgi_app()

