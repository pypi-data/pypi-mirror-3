"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE

    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')

    map.connect('/program', controller='program', action='index')
    map.connect('/schedule/{action}', controller='program')
    map.connect('/schedule', controller='program', action='edit')
    map.connect('/mobile', controller='jukebox', action='mobile')
    map.connect('/', controller='jukebox', action='index')
    map.connect('/{action}', controller='jukebox')
    map.connect('/findcover', controller='jukebox', action='findcover')
    map.connect('/cover/{artist}/{album}', controller='jukebox', action='cover')
    map.connect('/genre/{genreBase64}', controller='jukebox', action='genre')
    map.connect('/genre/', controller='jukebox', action='genre')
    map.connect('/artist/{artistBase64}', controller='jukebox', action='artist')
    map.connect('/artist/', controller='jukebox', action='artist')
    return map
