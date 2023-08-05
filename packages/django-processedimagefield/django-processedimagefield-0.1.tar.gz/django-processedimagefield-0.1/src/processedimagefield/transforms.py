from cStringIO import StringIO
from django.core.files.base import ContentFile
from PIL import Image


def jpeg(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.format = 'JPEG'
    return image


def thumbnail(image, width, height):
    image.thumbnail((width, height), Image.ANTIALIAS)
    return image
