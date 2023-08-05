from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields import files
from PIL import Image
from processedfilefield.mixins import ProcessedFieldFileMixin, ProcessedFileFieldMixin
import cStringIO
import os.path


class ProcessedImageFieldFile(ProcessedFieldFileMixin, files.ImageFieldFile):
    def transform(self, name, content, variation_name, transform):
        image = Image.open(content)
        image = transform(image)
        
        if not isinstance(image, Image.Image):
            raise ValueError('Variation "%s" didn\'t return a PIL.Image object' % (
                variation_name,
            ))
        elif not image.format:
            raise ValueError(
                'Variation "%s" returned an image without a file format. '
                'If creating a new image, the .format attribute should be set.' % (
                    variation_name,
                )
            )
        
        string_io = cStringIO.StringIO()
        image.save(string_io, image.format)
        
        content_file = ContentFile(string_io.getvalue())
        content_file.name = ''.join((os.path.splitext(name)[0], self.file_ext(image),))
        
        return content_file
    
    def file_ext(self, image):
        return '.%s' % (image.format.lower(),)


class ProcessedImageField(ProcessedFileFieldMixin, models.ImageField):
    attr_class = ProcessedImageFieldFile
