import logging
import os

import Image


log = logging.getLogger(__name__)

def convert(infilename, target_type='png'):
    '''Convert an image from one type to another.

    This uses PIL to convert an input file into another
    type.

    :param infilename: The name of the file to convert.
    :param target_type: The new image type to save as.
    '''

    outfilename = '{}.{}'.format(
        os.path.splitext(infilename)[0],
        target_type)

    log.info('Converting {} to {}.'.format(
            infilename,
            outfilename))

    im = Image.open(infilename)
    im.save(outfilename)

    return outfilename
