'''This implements a search method using flickr.com.

This is built on and completely indebted to the work done by James
Clarke on the flickr module contained in this package.
'''

from .flickr import photos_search


def search(tag):
    '''Search flickr for photos matching a tag.

    Returns the URL of the first matching photo, or None if no matches
    are found.
    '''

    photos = photos_search(tags=tag, per_page=1)
    if not photos:
        return None

    # Find the largest available version of this file.
    sizes = photos[0].getSizes()
    sizes.sort(key=lambda size: size['width'], reverse=True)

    return photos[0].getURL(
        size=sizes[0]['label'],
        urlType='source')
