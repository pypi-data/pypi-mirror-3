"""
PhantomJS rendering of page fragments.
"""

import os
import resource
import subprocess
import tempfile
import json
import logging

from PIL import Image
import cStringIO as StringIO

from .cache import cache_region, EPHEMERAL, SHARDS

log = logging.getLogger(__name__)

def setlimits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

@cache_region(SHARDS)
def render(phantomjs, rasterize, config):
    return render_uncached(phantomjs, rasterize, config)

def render_uncached(phantomjs, rasterize, config):
    """
    Render page to image
    """
    with tempfile.NamedTemporaryFile(suffix=".png") as image:
        config['file'] = image.name        
        # XXX if it hangs, we hang. .communicate() -> (stdoutdata, stderrdata)
        # XXX disk-cache can be too aggressive (should turn off caching on our local static stuff)
        rasterizer = subprocess.Popen(
        	[phantomjs, "--disk-cache=yes", rasterize, json.dumps(config)],
        	preexec_fn=setlimits)
        try:
            log.debug(rasterizer.communicate())
            errcode = rasterizer.wait()
            if errcode == 0:
                data = image.read()
                if data:
                    return data
        except IOError, e:
            log.warn(e)
        # XXX don't cache placeholder?
        return placeholder(config['width'], config['height'])

@cache_region(EPHEMERAL)
def placeholder(width, height):
    """Generate placeholder image in case of error..."""
    output = StringIO.StringIO()
    empty = Image.open(os.path.join(
        os.path.dirname(__file__), 'static', 'empty1.png'))
    if not (width and height):
        blank = empty
    else:
        blank = Image.new('RGBA', (width, height), '#fff')
        # 'empty' graphic also used as the alpha mask:
        blank.paste(empty, (width - empty.size[0], height - empty.size[1]), empty)
    blank.save(output, "PNG")
    value = output.getvalue()
    output.close()
    return value

@cache_region(EPHEMERAL)
def render_thumbnail(phantomjs, rasterize, config, size=(512, 512)):
    """
    Render page to a smaller image.
    """
    input = StringIO.StringIO(render(phantomjs, rasterize, config))
    # IOError "cannot identify image file"...
    im = Image.open(input)
    im.thumbnail(size, Image.ANTIALIAS)
    output = StringIO.StringIO()
    im.save(output, "PNG")
    input.close()
    value = output.getvalue()
    output.close()
    return value
    
