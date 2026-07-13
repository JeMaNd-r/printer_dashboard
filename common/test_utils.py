from collections import OrderedDict
from typing import Union

from django.db import models
from django.db.models import QuerySet


class CompareModelObjectsMixin:
    def assertListContains(self, expected: list, result: list) -> None:  # noqa N802
        """
        Asserts that the expected list is a subset of the result list.

        Parameters
        ----------
        expected : list
            The expected sub-list or item in the list.
        result : list
            The actual result list.

        Examples
        ----------
            >>> self.assertListContains([1, 2], [1, 2, 3])
            None
            >>> self.assertListContains([1, 2, 3], [1, 2])
            Traceback (most recent call last):
            ...
            AssertionError:
        """
        self.assertTrue(
            all([i in result for i in expected]),
            f"\nExpected sub-list/item: {expected}\nActual result: {result}",
        )

    def assertModelObjectsListEqual(  # noqa N802
        self, expected: list[Union[dict, object]], result: list[Union[dict, object]] | QuerySet
    ) -> None:
        """
        Compares a list of objects with another list of objects. If the objects are not
        of type `dict` or `OrderedDict` type, `dict(instance)` is used. If it is a model
        instance, `.__dict__` is used. If a key is not present in  object of the
        expected list, it is ignored. For example this is good for excluding created_at
        and updated_at fields in comparison.

        :param expected: The expected list of objects. Keys that are not present in the
            objects of this list areignored.
        :param result: The actual result list of objects.

        **Examples**:

            >>> self.assertModelObjectsListEqual(
            >>>     [{"a":1}, {"a":2}], [{"a":1}, {"a":3}]
            >>> ) # Fails
            Traceback (most recent call last):
            ...
            AssertionError:
            >>> self.assertModelObjectsListEqual(
            >>>     [{"a":1}, {"a":2}], [{"a":1}, {"a":2}]
            >>> )
            None
            >>> self.assertModelObjectsListEqual(
            >>>     [{"a":1}, {"a":2}], [{"a":1}, {"b":1}]
            >>> )
            None
        """
        self.assertEqual(
            len(expected),
            len(result),
            f"\nExpected: {expected}\nActual result: {result}",
        )
        for n1, n2 in zip(expected, result):
            if type(n1) is list and type(n2) is list:
                self.assertModelObjectsListEqual(n1, n2)
            else:
                self.assertModelObjectEquals(n1, n2)

    def assertModelObjectEquals(  # noqa N802
        self,
        expected: Union[dict, object],
        result: Union[dict, object],
    ) -> None:
        """
        Compares an object with another object. If the objects are not of type `dict`
        or `OrderedDict` type, `dict(instance)` is used. If it is a model instance,
        `.__dict__` is used. If a key is not present in the
        expected object, it is ignored. For example this is good for excluding
        created_at and updated_at fields in comparison.

        :param expected: The expected object. Keys that are not present in this object
            are ignored.
        :param result: The actual result object.

        Examples:
        ----------

        >>> self.assertModelObjectEquals({"a": 1, "b": 2}, {"a": 1, "b": 3})  # Fails
        Traceback (most recent call last):
        ...
        AssertionError:
        >>> self.assertModelObjectEquals(
        >>>     {"a":1}, {"a":1, "b":2}
        >>> ) # Succeeds because b is ignored
        None
        >>> self.assertModelObjectEquals({"a": 1, "b": 2}, {"a": 1, "b": 2})
        None
        >>> self.assertModelObjectEquals({"a": 1, "b": 2}, {"a": 1, "c": 1})
        None
        """
        assert type(expected) is not list and type(result) is not list, "Use assertModelObjectsListEqual for lists"
        d1, d2 = self.__compare(expected, result)
        self.assertEqual(len(d1), 0, f"\nExpected: {d1}\nActual result: {d2}")
        self.assertEqual(len(d2), 0, f"\nExpected: {d1}\nActual result: {d2}")

    def __to_dict(self, obj: Union[dict, object, None]) -> dict:
        try:
            return obj if type(obj) in (dict, OrderedDict) else dict(obj)
        except TypeError:  # Model instances
            return obj.__dict__
        except ValueError:
            if type(obj) is list:
                raise AssertionError(
                    f"Could not convert '{obj}' to dict. Did you mean \
                        .assertModelObjectsListEqual?"
                )
            raise AssertionError(f"Could not convert '{type(obj).__name__}' to dict. Object: '{obj}'")

    def __is_assert_equal(self, obj_1, obj_2):
        """Can the objects be compared with assertEqual?"""
        return (
            (
                type(obj_1) not in [dict, OrderedDict, list]
                and type(obj_2) not in [dict, OrderedDict, list]
                and not issubclass(type(obj_1), models.Model)
                and not issubclass(type(obj_2), models.Model)
            )
            or obj_1 is None
            or obj_2 is None
        )

    def __is_list_equal(self, obj_1, obj_2):
        """Can the objects be compared with assertModelObjectsListEqual?"""
        return type(obj_1) is list and type(obj_2) is list

    def __compare(
        self,
        obj_1: Union[dict, list, object, None],
        obj_2: Union[dict, list, object, None],
    ) -> tuple[dict, dict]:
        old = {}
        new = {}

        if self.__is_assert_equal(obj_1, obj_2):
            self.assertEqual(obj_1, obj_2)
            return old, new

        if self.__is_list_equal(obj_1, obj_2):
            self.assertModelObjectsListEqual(obj_1, obj_2)

        d1 = self.__to_dict(obj_1)
        d2 = self.__to_dict(obj_2)

        for k, v in d1.items():
            if type(v) is dict:
                try:
                    if k in d2:
                        self.assertModelObjectEquals(v, d2[k])
                    else:
                        self.assertModelObjectEquals(v, getattr(obj_2, k))  # This is a model instance
                except AssertionError as e:
                    raise AssertionError(f"Dictionary comparison failed for key {k}:\n\t{e}")
            elif type(v) is list:
                try:
                    self.assertModelObjectsListEqual(v, d2[k])
                except AssertionError as e:
                    raise AssertionError(f"List comparison failed for key {k}:\n\t{e}")
                except KeyError:
                    old.update({k: v})
            else:
                try:
                    if v != d2[k]:
                        old.update({k: v})
                        new.update({k: d2[k]})
                except KeyError:
                    old.update({k: v})

        return old, new
