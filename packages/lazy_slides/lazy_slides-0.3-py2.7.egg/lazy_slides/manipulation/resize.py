import logging

import Image


log = logging.getLogger(__name__)

def resize(infilename,
           outfilename,
           new_size):
    '''Resize an image file.

    :param infilename: The input image file name.
    :param outfilename: The output image file name.
    :param new_size: A tuple (width, height) of the new image size.
    '''

    log.info('Resizing {} to {}. New size = {}'.format(
            infilename,
            outfilename,
            new_size))

    im = Image.open(infilename)
    im_resized = im.resize(new_size)
    im_resized.save(outfilename)

    return outfilename
