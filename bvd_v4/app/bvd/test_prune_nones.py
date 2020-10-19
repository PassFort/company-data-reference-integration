from unittest import TestCase

from app.bvd.client import prune_nones


class TestPruneNones(TestCase):
    def test_prunes_simple_dict(self):
        test_dict = {"a": 1, "b": None, "c": 3}
        pruned = prune_nones(test_dict)

        self.assertEqual(pruned["a"], test_dict["a"])
        self.assertRaises(KeyError, lambda: pruned["b"])
        self.assertEqual(pruned["c"], test_dict["c"])

    def test_prunes_nested_dict(self):
        test_dict = {"a": 1, "b": {"d": 2, "e": None}, "c": 3}
        pruned = prune_nones(test_dict)

        self.assertDictEqual(pruned, {"a": 1, "b": {"d": 2}, "c": 3})

    def test_doesnt_prune_from_list(self):
        test_list = [1, None, 3]
        pruned = prune_nones(test_list)

        self.assertListEqual(pruned, [1, None, 3])

    def test_prunes_complex_nested(self):
        test_dict = {"a": 1, "b": [None, {"d": 2, "e": None}], "c": 3}
        pruned = prune_nones(test_dict)

        self.assertDictEqual(pruned, {"a": 1, "b": [None, {"d": 2}], "c": 3})
