"""
Input parsers.

If the input cannot be decoded, a ClaunIOError should be raised.
"""

from claun.core.communication.io import ClaunIOError
import json
from urlparse import parse_qs

def application_json(contents, **kwargs):
    """
    Tries to convert `contents` JSON string to python objects.

    Uses json library's loads function. Raises ClaunIOError if contents cannot be decoded.

    :param contents: Data to convert from json
    :param kwargs: Other parameters, they are passed to json.loads method.
    :return: Some python data structure.
    """
    try:
        return json.loads(contents, **kwargs)
    except Exception as e:
        raise ClaunIOError(e)

def application_x_www_form_urlencoded(contents, **kwargs):
    """
    Experimental. Probably does not work on complex data.
    """
    try:
        return parse_qs(contents, **kwargs)
    except Exception as e:
        raise ClaunIOError(e)

def text_plain(contents, **kwargs):
    """
    Does nothing.
    """
    return contents