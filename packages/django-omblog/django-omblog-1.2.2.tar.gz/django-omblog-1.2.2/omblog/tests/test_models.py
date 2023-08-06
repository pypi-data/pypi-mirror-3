from django.test import TestCase
from omblog.models import Post


class ModelTestCases(TestCase):

    def test_edit_url(self):
        """edit url returns correctly"""
        p = Post()
        p.title  = '1'
        p.slug = '1'
        p.content = '1'
        p.save()
        # edit url is correct
        self.assertEqual(
                p.edit_url(),
                '/admin/omblog/post/1/')


