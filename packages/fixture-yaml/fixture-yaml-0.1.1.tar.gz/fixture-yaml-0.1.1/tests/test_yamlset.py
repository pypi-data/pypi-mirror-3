import yaml

from nose.tools import assert_equals, assert_true
from pkg_resources import resource_filename
from unittest import TestCase

from fixture.loadable.loadable import LoadableFixture
from fixture_yaml import YAMLSet


class YAMLSetTest(TestCase):
    def test_iter(self):
        dataset = YAMLSet(resource_filename(__name__, 'test.yml'))
        data = yaml.load(open(resource_filename(__name__, 'test.yml'), 'r'))
        assert_equals(len(list(dataset)), len(data.keys()))

    def test_access(self):
        dataset = YAMLSet(resource_filename(__name__, 'test.yml'))
        assert_equals(dataset.Test1.name, 'Test 1')
        assert_equals(dataset.Test2.name, 'Test 2')

    def test_load(self):
        dataset1 = YAMLSet(resource_filename(__name__, 'test.yml'))
        dataset2 = YAMLSet(resource_filename(__name__, 'test2.yml'))
        fixture = TestLoadableFixture()
        data = fixture.data(dataset1, dataset2)
        data.setup()

        for dataset in (dataset1, dataset2):
            assert_true(dataset in fixture.media)
            rows = fixture.media[dataset]
            assert_equals(len(rows), len(list(dataset)))
            for row, (key, item) in zip(rows, dataset):
                assert_equals(row.id, item.id)
                assert_equals(row.name, item.name)


class TestStorageMedium(list):
    """
    List-like storage medium for testing purposes.
    """
    def visit_loader(self, loader):
        pass

    def save(self, row, column_vals):
        self.append(row)


class TestLoadableFixture(LoadableFixture):
    """
    Dummy :class:`LoadableFixture` implementation for testing purposes.
    """
    def __init__(self):
        self.media = {}
        self.loader = self

    def rollback(self):
        pass

    def commit(self):
        pass

    def attach_storage_medium(self, ds):
        if ds in self.media:
            medium = self.media[ds]
        else:
            self.media[ds] = medium = TestStorageMedium()
        ds.meta.storage_medium = medium

    def resolve_stored_object(self, column_val):
        return column_val
