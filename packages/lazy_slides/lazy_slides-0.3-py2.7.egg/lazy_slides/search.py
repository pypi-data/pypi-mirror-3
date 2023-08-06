import logging

from . import flickr


log = logging.getLogger(__name__)

# This gets set to the actual search function, i.e. the function which
# takes in a tag and finds a matching URL.
search_function = None

def search(tag):
    '''Search for an image file matching a given tag using the
    configured search function.

    This uses `search_function` to do the actual search, so make sure
    it's set before you use this.

    :param tag: The tag to search on.
    :raise ValueError: The search function is not set.
    :raise KeyError: No match is found for `tag`.
    :return: A URL.
    '''
    log.info('search function: {}.{}'.format(
            search_function.__module__,
            search_function.__name__))

    if search_function is None:
        raise ValueError(
            'You need to set lazy_slides.search.search_function before '
            'using search_photos()!')

    log.info('searching for images tagged with "{}"'.format(tag))
    url = search_function(tag=tag)

    if url is None:
        raise KeyError('No results for "{}"'.format(tag))

    log.info('found photo: {}'.format(url))
    return url
