import logging

log = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPSeeOther
from jinja2.utils import Markup 
from deform import Form, ValidationFailure
from . import schema, tables
from .phantom import render, render_uncached, render_thumbnail
import time
import json

# Unique ID for RSS: int(time.time() / RSS_GUID_SECONDS)
# (Now this is the greater of slide.duration or RSS_GUID_SECONDS)
RSS_GUID_SECONDS = 60

import re

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', s) ]

def home(request):
    return {'title':'Sharder'}

def edit_shard(request): 
    shard = request.context
    shardform = Form(schema.Shard(), buttons=('submit',))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = shardform.validate(controls)
            shard.name = appstruct['name']
            shard.url = appstruct['url']
            shard.selector = appstruct['selector']
            shard.width = appstruct['width']
            shard.height = appstruct['height']
            shard.triggers = appstruct['triggers']
        except ValidationFailure, e:
            return {'form':Markup(e.render())}
        
    appstruct = dict(name=shard.name,
                     url=shard.url,
                     selector=shard.selector,
                     width=shard.width,
                     height=shard.height,
                     triggers=shard.triggers,
                     )
    return {'form':Markup(shardform.render(appstruct)),
            'shard':u'%s/shards/%d/preview' % (request.application_url, shard.id),
            'shard_full':u'%s/shards/%d' % (request.application_url, shard.id),
            'title':'Edit Shard'}

def new_shard(request):
    shardform = Form(schema.Shard(), buttons=('submit',))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = shardform.validate(controls)
            newshard = tables.Shard(name=appstruct['name'],
                                  url=appstruct['url'],
                                  selector=appstruct['selector'],
                                  width=appstruct['width'],
                                  height=appstruct['height'],
                                  triggers=appstruct['triggers'],
                                  )
            tables.DBSession.add(newshard)
            tables.DBSession.flush()
            location = u"%s/shards/%d/edit" % \
                (request.application_url, newshard.id)
            log.debug(u"new shard at %s", location)
            return HTTPSeeOther(location)
        except ValidationFailure, e:
            return {'form':Markup(e.render())}
    return {'form':Markup(shardform.render())}

def shard(request):
    """Return a picture of part of a page."""
    settings = request.registry.settings
    phantomjs = settings['phantomjs']
    rasterize = settings['rasterize']
    
    context = request.context
    
    config = {}
    config['jquery'] = request.registry.settings['jquery']
    config['url'] = context.url
    config['width'] = context.width or None
    config['height'] = context.height or None
    config['selector'] = context.selector
    if context.selector in (u'html', u'*') and context.width and context.height:
        config['viewportSize'] = dict(width=context.width, height=context.height)
    else:
        config['viewportSize'] = dict(width=600, height=600)
    config['triggers'] = context.triggers
    
    log.debug(json.dumps(config))
    
    if request.view_name == 'preview':
        request.response.body = render_thumbnail(phantomjs, rasterize, config, (512,512))
    else:
        if 'uncached' in request.GET:
            render_func = render_uncached
        else:
            render_func = render
        request.response.body = render_func(phantomjs, rasterize, config)
            
    request.response.content_type = 'image/png'
    request.response.charset = None
    return request.response

def new_slideshow(request):
    shardform = Form(schema.Slideshow(), buttons=('submit',))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = shardform.validate(controls)
            slideshow = tables.Slideshow(name=appstruct['name'])
            for i, data in enumerate(appstruct['slides']):
                slide = tables.Slide(duration=data['duration'],
                                     shard_id=data['shard'],
                                     order=i)
                slideshow.slides.append(slide)
            tables.DBSession.add(slideshow)
            tables.DBSession.flush()
            location = u"%s/shows/%d/edit" % \
                (request.application_url, slideshow.id)
            return HTTPSeeOther(location=location)
        except ValidationFailure, e:
            return {'form':Markup(e.render())}
    return {'form':Markup(shardform.render())}

    links = []
    for shard in tables.DBSession.query(tables.Shard).all():
        links.append(dict(name=shard.name, link=u"%s/%d/edit" % 
                          (request.url.rstrip('/'), shard.id), id=shard.id))                            
    return {'links':links, 'title':'Shards'}

def edit_slideshow(request):
    context = request.context
    form = Form(schema.Slideshow(), buttons=('submit',))
    appstruct = {'name':context.name, 
                 'slides':[dict(shard=slide.shard_id, duration=slide.duration) for slide in context.slides]}
    return {'form':form.render(appstruct), 'title':'Edit Slideshow'}

def edit_slideshow_POST(request):
    slideshow = request.context
    form = Form(schema.Slideshow(), buttons=('submit',))
    controls = request.POST.items()
    try:
        for slide in slideshow.slides:
            request.db.delete(slide)
        slideshow.slides = []
        appstruct = form.validate(controls)
        for i, data in enumerate(appstruct['slides']):
            slide = tables.Slide(duration=data['duration'],
                                 shard_id=data['shard'],
                                 order=i)
            slideshow.slides.append(slide)
        return HTTPSeeOther(location=request.url)
    except ValidationFailure, e:
        return {'form':Markup(e.render()), 'title':'Edit Slideshow'}
        
def shows(request):
    links = []
    context = request.context
    for item in tables.DBSession.query(context.__model__).all():
        links.append(dict(name=item.name, 
                          link=request.resource_url(context, item.id, 'edit'), 
                          id=item.id))
    return {'links':links, 'title':'Shows'}

def shards(request):
    rc = shows(request)
    rc['title'] = 'Shards'
    return rc

def slideshow(request):
    """Render slideshow to mRSS"""
    slideshow = request.context
    items = []
    data = dict(name=slideshow.name,
                title=slideshow.name,            
                link=request.url,
                description=u'Slideshow',
                items=items,
                ttl=2)
    for slide in slideshow.slides:
        shard = slide.shard
        shard_url = u"%s/shards/%d.png?rnd=%s" % (request.application_url, 
                shard.id, 
                int(time.time() / max(slide.duration, RSS_GUID_SECONDS)))
        item_data = dict(title=shard.name,
                         link=shard_url,
                         url=shard_url,
                         duration=slide.duration,
                         type=u'image/png')
        items.append(item_data)
    request.response.content_type = 'application/rss+xml'
    return data
