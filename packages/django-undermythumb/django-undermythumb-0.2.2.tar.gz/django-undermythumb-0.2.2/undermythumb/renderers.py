try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import struct

from django.core.files.base import ContentFile

from PIL import Image, ImageOps


class BaseRenderer(object):
    """Base class for renderers. 

    Subclass this to build your own renderers.
    """

    def __init__(self, format='jpg', quality=100, force_rgb=True,
                 *args, **kwargs):
        self.format = format
        self.quality = quality
        self.force_rgb = force_rgb
        self.options = kwargs

    def _normalize_format(self):
        format = self.format.upper()
        if format in ['JPG']:
            format = 'JPEG'
        return format

    def _create_tmp_image(self, content):
        """Creates a temporary image for manipulation, and handles
        optional RGB conversion.
        """

        content.seek(0)
        image = Image.open(content)
        if self.force_rgb and image.mode not in ('L', 'RGB', 'RGBA'):
            image = image.convert('RGB')
        return image

    def _create_content_file(self, content):
        """Returns image data as a ``ContentFile``.
        """

        io = StringIO()
        content.save(io, self._normalize_format(), quality=self.quality)
        return ContentFile(io.getvalue())

    def generate(self, content):
        """Resizes a valid image, and returns as a Django ``ContentFile``.
        """

        tmp = self._create_tmp_image(content)
        rendered = self._render(tmp)
        return self._create_content_file(rendered)

    def _render(self, image):
        """Renders the image. Override this method when creating 
        a custom renderer.
        """

        raise NotImplementedError('Override this method to render images!')


class CropRenderer(BaseRenderer):
    """Renders an image cropped to a given width and height.
    """

    def __init__(self, width, height, *args, **kwargs):
        self.width = int(width)
        self.height = int(height)
        super(CropRenderer, self).__init__(*args, **kwargs)

    def _render(self, image):
        return ImageOps.fit(image, (self.width, self.height),
                            Image.ANTIALIAS, 0, (0.5, 0.5))


class ResizeRenderer(BaseRenderer):
    """Resizes an image to a given width and height.

    The image will maintain its aspect ratio unless ``constrain``
    is ``False``, and not be resized above it's dimensions unless
    ``upscale`` is ``True``.
    """

    def __init__(self, width, height, constrain=True, upscale=False,
                 *args, **kwargs):
        self.width = width
        self.height = height
        self.constrain = constrain
        self.upscale = upscale

        super(ResizeRenderer, self).__init__(*args, **kwargs)

    def _render(self, image):
        dw, dh = self.width, self.height
        sw, sh = image.size
        
        if self.constrain:
            sr = float(sw) / float(sh)
            if sw > sh:
                dh = dw / sr
            else:
                dh = dw * sr

        # resize if the source dimensions are smaller than the desired,
        # or the user has approved scaling the image above 
        # it's original dimensions
        if ((((dw > sw) or (dh > sh)) and self.upscale) or
            ((dw < sw) or (dh < sh))):
            image = image.resize((int(dw), int(dh)), Image.ANTIALIAS)

        return image


class LetterboxRenderer(ResizeRenderer):
    """Resizes an image to a given width and height using the ``ResizeRenderer``, 
    and places it on a colored canvas. 

    Cavas color is defined as a hexidecimal color value.

    Example: ::

        LetterboxRenderer(150, 150, bg_color='#000000')

    """
    
    def __init__(self, width, height, bg_color='#FFFFFF', *args, **kwargs):                 
        super(LetterboxRenderer, self).__init__(width, height, *args, 
                                                **kwargs)

        # convert hex string to rgba quad
        bg_color = bg_color.strip('#')
        bg_hex = bg_color.decode('hex')
        self.bg_color = struct.unpack('BBB', bg_hex) + (0, )

    def _render(self, image):
        image = super(LetterboxRenderer, self)._render(image)
        src_w, src_h = image.size

        # place image on canvas and save
        canvas = Image.new('RGBA', (self.width, self.height), self.bg_color)                           
        paste_x = (self.width - src_w) / 2
        paste_y = (self.height - src_h) / 2
        canvas.paste(image, (paste_x, paste_y))

        return canvas
