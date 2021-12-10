#!/usr/bin/env python3

"""A pickle-able minimal representation of a QgsGeometry/QgsFeature."""

import math

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsDistanceArea,
    QgsGeometry,
    QgsVertexId
)

from .vertices import Vertices


class CartogramFeature:
    """A pickle-able minimal representation of a QgsGeometry/QgsFeature."""
    def __init__(self, feature_id, wkt, crs, value):
        """
        A picke-able minimal representation of a QgsGeometry/QgsFeature.

        Arguments
        ---------
            feature_id : int
                feature id
            wkt : str
                geometry in WKT format
            crs : str
                cartographic reference system in Proj4 format
            value : float
                value of the field that defines the distortion of the cartogram
        """
        self.id = feature_id
        self.wkt = wkt
        self.crs = crs
        self.value = value
        self._force_multipolygon = (wkt[:12].upper() == "MULTIPOLYGON")

    @property
    def area(self):
        try:
            return self._area
        except AttributeError:
            self._recompute_area_radius_centroid()
            return self._area

    @property
    def area_value_ratio(self):
        return self._area_value_ratio

    @area_value_ratio.setter
    def area_value_ratio(self, area_value_ratio):
        self._area_value_ratio = area_value_ratio
        try:
            del self._mass, self._sizeerror
        except AttributeError:
            pass

    @property
    def cx(self):
        try:
            return self._cx
        except AttributeError:
            self._recompute_area_radius_centroid()
            return self._cx

    @property
    def cy(self):
        try:
            return self._cy
        except AttributeError:
            self._recompute_area_radius_centroid()
            return self._cy

    @property
    def geometry(self):
        return QgsGeometry().fromWkt(self.wkt)

    @property
    def mass(self):
        try:
            return self._mass
        except AttributeError:
            self._recompute_mass_sizeerror()
            return self._mass

    @property
    def radius(self):
        try:
            return self._radius
        except AttributeError:
            self._recompute_area_radius_centroid()
            return self._radius

    @property
    def sizeerror(self):
        try:
            return self._sizeerror
        except AttributeError:
            self._recompute_mass_sizeerror()
            return self._sizeerror

    @property
    def vertices(self):
        try:
            return self._vertices
        except AttributeError:
            self._vertices = Vertices(self.geometry)
            return self._vertices

    @property
    def wkt(self):
        try:
            return self._wkt
        except AttributeError:
            self._wkt = self._vertices.as_wkt(self._force_multipolygon)
            return self._wkt

    @wkt.setter
    def wkt(self, wkt):
        self._wkt = wkt
        try:
            del self._area, self._radius, self._cx, self._cy
        except AttributeError:
            pass

    def _recompute_mass_sizeerror(self):
        target_area = self.value * self._area_value_ratio
        if target_area == 0:
            self._mass = 0
        else:
            self._mass = math.sqrt(target_area / math.pi) - self.radius
        self._sizeerror = (
            max(self.area, target_area)
            / min(self.area, target_area)
        )

    def _recompute_area_radius_centroid(self):
        geometry = self.geometry
        crs = QgsCoordinateReferenceSystem.fromProj(self.crs)
        distance_area_calculator = QgsDistanceArea()
        distance_area_calculator.setSourceCrs(crs, QgsCoordinateTransformContext())
        distance_area_calculator.setEllipsoid("WGS84")

        # recompute area
        self._area = distance_area_calculator.measureArea(geometry)

        # recompute radius
        if self._area == 0:
            self._radius = 0
        else:
            self._radius = math.sqrt(self._area / math.pi)

        # recompute centroid
        centroid = geometry.centroid().asPoint()
        self._cx = centroid.x()
        self._cy = centroid.y()

    @staticmethod
    def _vertex_id(part, ring, vertex):
        vertex_id = QgsVertexId(part, ring, vertex, QgsVertexId.SegmentVertex)
        if not vertex_id.IsValid():
            vertex_id = QgsVertexId(part, ring, vertex, QgsVertexId.CurveVertex)
            if not vertex_id.IsValid():
                raise ValueError("Invalid vertex addressing.")
        return vertex_id
