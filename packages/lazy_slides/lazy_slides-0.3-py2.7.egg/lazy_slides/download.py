import contextlib
import logging
import os
import urllib2
import urlparse
import uuid


log = logging.getLogger(__name__)

def download(url, directory):
    '''Download a file specified by a URL to a local file.

    This generates a unique name for the downloaded file and saves
    into that.

    :param url: The URL to download.
    :param directory: The directory into which to save the file.
    '''

    parsed = urlparse.urlparse(url)

    # Calculate the save-file name
    filename = os.path.split(parsed.path)[1]
    filename_comps = os.path.splitext(filename)
    filename = '{}_{}{}'.format(
        filename_comps[0],
        uuid.uuid4(),
        filename_comps[1])
    filename = os.path.join(directory, filename)

    log.info('Downloading {} to {}'.format(
            url, filename))

    # Save the URL data to the new filename.
    with contextlib.closing(urllib2.urlopen(url)) as infile:
        with open(filename, 'wb') as outfile:
            outfile.write(infile.read())

    return filename
