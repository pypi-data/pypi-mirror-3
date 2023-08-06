"""
Input parsers.

If the input cannot be decoded, a ClaunIOError should be raised.
"""

from claun.core import container
from claun.core.communication.io import ClaunIOError

import json
from urllib import urlencode

def application_json(contents, **kwargs):
    """
    Converts `contents` to json string and adds the proper HTTP header.

    Uses json library's dumps function, does not catch any exceptions.

    :param contents: Data to convert to json
    :param kwargs: Other parameters, they are passed to json.dumps method.
    :return: JSON string
    """
    try:
        container.web.header("Content-Type", "application/json;charset=utf-8", True) # True means no overriding/appending
    except AttributeError: # sometimes web.py does not see ctx.headers property
        pass
    try:
        return json.dumps(contents, **kwargs)
    except Exception as e:
        raise ClaunIOError(e)

def application_x_www_form_urlencoded(contents, **kwargs):
    """
    Experimental. Probably does not work on complex data.
    """
    try:
        container.web.header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8", True) # True means no overriding/appending
    except AttributeError: # sometimes web.py does not see ctx.headers property
        pass
    try:
        return urlencode(contents, **kwargs)
    except Exception as e:
        raise ClaunIOError(e)

def text_plain(contents, **kwargs):
    """
    Does nothing.
    """
    return contents