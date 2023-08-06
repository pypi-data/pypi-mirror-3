from reportlab.pdfgen import canvas

def generate_slides(tags,
                    tag_map,
                    outfile,
                    args):
    '''Generate a beamer slideshow.

    :param tags: The tags used to find the images in the slideshow.
    :param filenames: The filenames of the images for the slideshow.
    :param outfile: The name of the file into which the results should
      be saved.
    '''
    c = canvas.Canvas(outfile)
    for tag in tags:
        c.setPageSize((args.image_width,
                       args.image_height))
        c.drawImage(tag_map[tag], 0, 0)
        c.showPage()

    c.save()

