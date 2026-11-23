'''
Shared image helpers used by the forms that accept photos
'''
from PIL import Image, ImageOps


def crop_and_resize(path, x=None, y=None, width=None, height=None, size=500):
    '''
    Crop the image saved at path to the given box (when one is given),
    then resize it to a square of size x size pixels and save it in place.
    Returns True when the image was processed, False otherwise.
    '''
    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            if None not in (x, y, width, height) and width > 0 and height > 0:
                image = image.crop((
                                int(x), int(y),
                                int(x + width), int(y + height)))
            else:
                image = ImageOps.fit(image, (min(image.size), ) * 2)
            image = image.resize((size, size), Image.Resampling.LANCZOS)
            if image.mode not in ('RGB', 'RGBA', 'L'):
                image = image.convert('RGB')
            image.save(path)
        return True
    except (OSError, ValueError):
        return False
