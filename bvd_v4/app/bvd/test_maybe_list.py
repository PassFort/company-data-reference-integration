from unittest import TestCase

from schematics import Model
from schematics.exceptions import DataError
from schematics.types import IntType, StringType

from app.bvd.maybe_list import MaybeListType


class TestMaybeList(TestCase):
    def test_doesnt_coerce_none(self):
        class TestModel(Model):
            field = MaybeListType(IntType, default=list)

        instance = TestModel({"field": None})
        self.assertEqual(instance.field, None)

    def test_coerces_int_to_list(self):
        class TestModel(Model):
            field = MaybeListType(IntType)

        instance = TestModel({"field": 42})
        self.assertEqual(instance.field, [42])

    def test_coerces_string_to_list(self):
        class TestModel(Model):
            field = MaybeListType(StringType)

        instance = TestModel({"field": "a_string"})
        self.assertEqual(instance.field, ["a_string"])

    def test_does_nothing_to_empty_list(self):
        class TestModel(Model):
            field = MaybeListType(IntType)

        instance = TestModel({"field": []})
        self.assertEqual(instance.field, [])

    def test_does_nothing_to_list_with_content(self):
        class TestModel(Model):
            field = MaybeListType(IntType)

        instance = TestModel({"field": [1, 2, 3]})
        self.assertEqual(instance.field, [1, 2, 3])

    def test_can_pass_validation_after_coercion(self):
        class TestModel(Model):
            field = MaybeListType(IntType)

        TestModel({"field": 42}).validate()

    def test_unset_default_field(self):
        class TestModel(Model):
            field = MaybeListType(IntType)

        instance = TestModel({})
        self.assertEqual(instance.field, None)

    def test_set_default_field(self):
        class TestModel(Model):
            field = MaybeListType(IntType, default=list)

        instance = TestModel({})
        self.assertEqual(instance.field, [])
