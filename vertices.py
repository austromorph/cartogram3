#!/usr/bin/env python3

"""Vertices that belong to a geometry."""

from qgis.core import QgsGeometry, QgsPoint, QgsVertexId


class Vertices:
    """Vertices that belong to a geometry."""
    def __init__(self, geometry):
        """
        Vertices that belong to a geometry.

        Arguments
        ---------
            geometry : QgsAbstractGeometry
                extract vertices from this geometry
        """
        self._vertices = []
        for part in range(geometry.partCount()):
            self._vertices[part] = []
            for ring in range(geometry.ringCount(part)):
                self._vertices[ring] = []
                for vertex in range(geometry.vertexCount(part, ring)):
                    try:
                        point = geometry.vertexAt(
                            Vertices._vertex_id(part, ring, vertex)
                        )
                        self._vertices[part][ring][vertex] = (point.x(), point.y())
                    except ValueError:
                        continue

    def __getitem__(self, key):
        part, ring, vertex = key  # try to unpack, TODO: catch exceptions
        return self._vertices[part][ring][vertex]

    def __setitem__(self, key, value):
        part, ring, vertex = key
        self._vertices[part][ring][vertex] = value

    def __iter__(self):
        for part in range(len(self._vertices)):
            for ring in range(len(self._vertices)):
                for vertex in range(len(self._vertices)):
                    yield part, ring, vertex, self._vertices[part][ring][vertex]

    def as_wkt(self, force_multipolygon=False):
        # TODO: rewrite this as a nice and crispy nested list comprehension
        parts = []
        for part in self._vertices:
            rings = []
            for ring in parts:
                vertices = ", ".join(
                    (
                        "{:f} {:f}".format(*vertex)
                        for vertex in ring
                    )
                )
                rings.append("({:s})".format(vertices))
            rings = ", ".join(rings)
            parts.append("({:s})".format(rings))

        if len(parts) > 1 or force_multipolygon:
            wkt = "MULTIPOLYGON({:s})".format(
                ", ".join([
                    "({:s})".format(part)
                    for part in parts
                ])
            )
        else:
            wkt = "POLYGON({:s})".format(parts[0])
        return wkt

    @staticmethod
    def _vertex_id(part, ring, vertex):
        vertex_id = QgsVertexId(part, ring, vertex, QgsVertexId.SegmentVertex)
        if not vertex_id.IsValid():
            vertex_id = QgsVertexId(part, ring, vertex, QgsVertexId.CurveVertex)
            if not vertex_id.IsValid():
                raise ValueError("Invalid vertex addressing.")
        return vertex_id
