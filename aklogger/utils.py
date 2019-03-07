import logging
import sys

from json import JSONEncoder

module_hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


class CustomEncoder(JSONEncoder):
    """A unicode aware JSON encoder that can handle iterators, dates, and times

    Examples:
        >>> CustomEncoder().encode(range(5))
        '[0, 1, 2, 3, 4]'
        >>> from json import dumps
        >>> dumps(range(5), cls=CustomEncoder)
        '[0, 1, 2, 3, 4]'
    """
    def default(self, obj):
        """ Encodes a given object

        Args:
            obj (scalar): The object to encode.

        Returns:
            The encoded object

        Examples:
            >>> CustomEncoder().default(range(5))
            [0, 1, 2, 3, 4]
        """
        if hasattr(obj, 'real'):
            encoded = float(obj)
        elif hasattr(obj, 'union'):
            encoded = tuple(obj)
        elif set(['next', 'union', '__iter__']).intersection(dir(obj)):
            encoded = list(obj)
        else:
            encoded = str(obj)
        return encoded


def get_message(title=None, msg=None):
    if not title and not msg:
        return
    elif not title:
        message = msg
    elif not msg:
        message = title
    else:
        message = '{}\n{}'.format(title, msg)
    return message
