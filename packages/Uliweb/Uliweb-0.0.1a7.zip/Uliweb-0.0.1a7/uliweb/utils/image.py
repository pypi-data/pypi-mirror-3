import os

def fix_filename(filename, suffix=''):
    """
    e.g.
        fix_filename('icon.png', '_40x40')
        
        return
    
            icon_40x40.png
    """
    if suffix:
        f, ext = os.path.splitext(filename)
        return f+suffix+ext
    else:
        return filename
        
def resize_image(fobj, size=(50, 50)):
    import Image
    from StringIO import StringIO
    
    image = Image.open(fobj)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    image = image.resize(size, Image.ANTIALIAS)
    o = StringIO()
    image.save(o, "JPEG")
    o.seek(0)
    return o

def thumbnail_image(realfile, filename, size=(200, 75)):
    """
    :param: real input filename (string)
    :filename: relative input filename (string)
    
    return value should be a tuple, (saved_real_filename, saved_filename)
    """
    import Image

    im = Image.open(realfile)
    file, ext = os.path.splitext(realfile)
    if im.size[0]<=size[0] and im.size[1]<=size[1]:
        #the image size is smaller than thumbnail size, so we don't need to 
        #thumbnail the image
        return filename, filename
    im.thumbnail(size, Image.ANTIALIAS)
    format = ext[1:].upper()
    if format == 'JPG':
        format = 'JPEG'
    ofile = file + ".thumbnail" + ext
    im.save(ofile, format)
    file1, ext1 = os.path.splitext(filename)
    return ofile, file1 + ".thumbnail" + ext

def resize_image_string(buf, size=(50, 50)):
    from StringIO import StringIO
    f = StringIO(buf)
    return resize_image(f, size).getvalue()
    
def image_size(filename):
    import Image

    image = Image.open(filename)
    return image.size

def crop_resize(fobj, outfile, x, y, w, h, size=(50, 50)):
    import Image

    image = Image.open(fobj)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    r = image.crop((x, y, x+w, y+h))
    if size:
        rm = r.resize(size, Image.ANTIALIAS)
    rm.save(outfile, "JPEG")
    