"""Deform schemas for sharder"""

import colander
from . import tables

class Shard(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    url = colander.SchemaNode(colander.String())
    selector = colander.SchemaNode(colander.String(),
            description='jQuery selector, or * for entire page.')
    width = colander.SchemaNode(colander.Integer(),
            description='Resize selected element to this width (0 preserves width).',
            missing=0)
    height = colander.SchemaNode(colander.Integer(),
            description='Resize selected element to this height (0 preserves height).',
            missing=0)
    triggers = colander.SchemaNode(colander.Integer(),
       description='Number of "phantomjs screenshot" messages in page. '
       'Allows scripting to signal when screen is ready. '
       'Usually 0 or 1.',
       missing=0)

def shard_exists(node, value):
    if not tables.DBSession.query(tables.Shard.id).filter_by(id=value).all():
        raise colander.Invalid(node, "Shard %r does not exist" % value)

class Slide(colander.MappingSchema):
    duration = colander.SchemaNode(colander.Integer(), description="Duration in seconds")
    shard = colander.SchemaNode(colander.Integer(), validator=shard_exists)

class Slides(colander.SequenceSchema):
    slide = Slide()
    
class Slideshow(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    slides = Slides()
