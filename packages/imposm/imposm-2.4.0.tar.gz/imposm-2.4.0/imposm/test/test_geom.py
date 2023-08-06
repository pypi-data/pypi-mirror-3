from imposm.geom import LineStringBuilder
from shapely.ops import linemerge
from nose.tools import eq_

class TestLineStringBuilder(object):
    def test_split(self):
        builder = LineStringBuilder()
        geom = builder.to_geom([(0, 0), (1, 1), (2, 2), (3, 3)], max_length=3)
        assert isinstance(geom, list)
        eq_(len(geom), 2)
        
        merged = linemerge(geom)
        eq_(merged.type, 'LineString')

    def test_split(self):
        builder = LineStringBuilder()
        geom = builder.to_geom([(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], max_length=2)
        assert isinstance(geom, list)
        eq_(len(geom), 3)
        
        merged = linemerge(geom)
        eq_(merged.type, 'LineString')

    def test_split_same_length(self):
        builder = LineStringBuilder()
        geom = builder.to_geom([(0, 0), (1, 1), (2, 2), (3, 3)], max_length=4)
        eq_(geom.type, 'LineString')


    def test_split_short(self):
        builder = LineStringBuilder()
        geom = builder.to_geom([(0, 0), (1, 1), (2, 2), (3, 3)], max_length=10)
        eq_(geom.type, 'LineString')
