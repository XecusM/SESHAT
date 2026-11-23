import os
import tempfile

from PIL import Image
from django.test import SimpleTestCase

from seshat.images import crop_and_resize


class CropAndResizeTest(SimpleTestCase):
    '''
    Test the shared image helper
    '''

    def make_image(self, size=(800, 600)):
        handle, path = tempfile.mkstemp(suffix='.png')
        os.close(handle)
        Image.new('RGB', size, 'red').save(path)
        self.addCleanup(os.remove, path)
        return path

    def test_crop_box(self):
        path = self.make_image()
        self.assertTrue(crop_and_resize(path, 10, 10, 300, 300, size=200))
        with Image.open(path) as image:
            self.assertEqual(image.size, (200, 200))

    def test_without_crop_box_uses_center_square(self):
        path = self.make_image((900, 300))
        self.assertTrue(crop_and_resize(path, size=100))
        with Image.open(path) as image:
            self.assertEqual(image.size, (100, 100))

    def test_invalid_file(self):
        handle, path = tempfile.mkstemp(suffix='.png')
        os.write(handle, b'not an image')
        os.close(handle)
        self.addCleanup(os.remove, path)
        self.assertFalse(crop_and_resize(path))
