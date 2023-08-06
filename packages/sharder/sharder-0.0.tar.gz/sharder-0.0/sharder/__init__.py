import transaction
import zope.sqlalchemy
import stucco_evolution
import os

from pkg_resources import resource_filename
from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import static_view
import pyramid.authentication
import pyramid.authorization
import pyramid.request
from . import tables
from . import models
from . import security

import logging
log = logging.getLogger(__name__)

class Request(pyramid.request.Request):
    @reify
    def db(self):
        return tables.DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    tables.DBSession.configure(bind=engine)

    # bw compat
    settings['rasterize'] = resource_filename('sharder', 
                                              'support/rasterize.js')
    settings['jquery'] = resource_filename('sharder', 
                                           'support/jquery-1.6.4.min.js')
  
    with engine.begin() as connection:
        stucco_evolution.initialize(connection)
        stucco_evolution.create_or_upgrade_packages(connection, 'sharder')

    config = Configurator(settings=settings,
                          request_factory=Request,
                          root_factory=models.make(),
                          )
    config.add_static_view('static', 'sharder:static', cache_max_age=3600)
    config.add_static_view('deform', 'deform:static', cache_max_age=3600)

    config.include('pyramid_jinja2')
    
    config.add_view('.views.home',
                    context=models.Sharder,
                    renderer='home.jinja2')    

    # Shards:
    
    config.add_view('.views.shards',
                    context=models.Shards,
                    renderer='shards.jinja2')
        
    config.add_view('.views.new_shard',
                    context=models.Shards,
                    name='new',
                    renderer='new_shard.jinja2',
                    permission='post')

    config.add_view('.views.edit_shard',
                    context=tables.Shard,
                    name='edit',
                    renderer='edit_shard.jinja2',
                    permission='post')

    config.add_view('.views.shard',
                    context=tables.Shard)
    
    config.add_view('.views.shard',
                    name='preview',
                    context=tables.Shard)
    
    # Slideshows:
    
    config.add_view('.views.shows',
                    context=models.Shows,
                    renderer='shards.jinja2')

    config.add_view('.views.new_slideshow',
                    context=models.Shows,
                    name='new',
                    renderer='new_slideshow.jinja2',
                    permission='post')

    config.add_view('.views.edit_slideshow',
                    name='edit',
                    renderer='edit_shard.jinja2',
                    context=tables.Slideshow)

    config.add_view('.views.edit_slideshow_POST',
                    name='edit',
                    renderer='edit_shard.jinja2',
                    context=tables.Slideshow,
                    permission='post',
                    request_method='POST')

    config.add_view('.views.slideshow',
                    renderer='slideshow.jinja2',
                    context=tables.Slideshow)

    return config.make_wsgi_app()
