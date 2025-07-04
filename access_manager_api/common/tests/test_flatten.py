from common.flatten import flatten
from django.test import TestCase


class FlattenTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_flatten(self):
        self.assertEqual(
            flatten([[1, 2], [3, 4]]),
            [1, 2, 3, 4],
        )

        self.assertNotEqual(
            flatten([[1, 2], [3, 4]]),
            [1, 2, 3, 5],
        )
