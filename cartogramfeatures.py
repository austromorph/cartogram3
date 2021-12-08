#!/usr/bin/env python3


"""Handle a list of `CartogramFeature`."""


import functools
import itertools
import math
import multiprocessing

from .cartogramfeature import CartogramFeature


class CartogramFeatures:
    """Handle a list of `CartogramFeature`."""
    def __init__(self):
        """Handle a list of `CartogramFeature`."""
        self._features = {}
        self._layer = None  # not yet really kosher - in some cases, we remember the input layer
        self.workers = multiprocessing.get_context("spawn").Pool()

    # next two methods not alphabetical order, because they’re
    # instantiator and data output

    @staticmethod
    def from_polygon_layer(layer, field_name):
        cartogram_features = CartogramFeatures()
        cartogram_features._layer = layer
        crs = layer.sourceCrs().toProj()
        for feature in layer.getFeatures():
            feature_id = feature.id()
            cartogram_feature = CartogramFeature(
                feature_id,
                feature.geometry().asWkt(),
                crs,
                feature[field_name]
            )
            cartogram_features[feature_id] = cartogram_feature
        return cartogram_features

    def copy_geometries_back_to_layer(self):
        if not self._layer:
            raise NotImplementedError(
                "`copy_geometries_back_to_layer()` only works on instances "
                + "created with `from_polygon_layer()`"
            )
        for feature in self._layer.getFeatures():
            feature_id = feature.id()
            feature.geometry().set(self[feature_id].geometry)

    def __setitem__(self, feature_id, cartogram_feature):
        self._features[feature_id] = cartogram_feature

    def __getitem(self, feature_id):
        return self._features[feature_id]

    def __iter__(self):
        return self.values()

    @property
    def average_error(self):
        return self.total_value / len(self._features)

    def keys(self):
        for feature_id in self._features:
            yield feature_id

    def values(self):
        for feature_id in self._features:
            yield self._features[feature_id]

    @property
    def vertices(self):
        for feature_id in self._features:
            for part, ring, vertex, point in self._features[feature_id].vertices:
                yield feature_id, part, ring, vertex, point

    @property
    def total_area(self):
        total_area = sum(
            self.workers.imap(
                # lambda x: x.area,
                functools.partial(_getattr, name="area"),
                self
            )
        )
        return total_area

    @property
    def total_error(self):
        area_value_ratio = self.total_area / self.total_value
        for feature in self:
            feature.area_value_ratio = area_value_ratio
        total_error = sum(
            self.workers.imap(
                # lambda x: x.sizeerror,
                functools.partial(_getattr, name="sizeerror"),
                self
            )
        )
        return total_error

    @property
    @functools.cache
    def total_value(self):
        total_value = sum(
            self.workers.imap(
                # lambda x: x.value,
                functools.partial(_getattr, name="value"),
                self
            )
        )
        return total_value

    def transform(self, max_iterations=10, max_average_error=0.1):
        iteration = 0
        average_error = self.average_error

        while (
                iteration < max_iterations
                and average_error > max_average_error
        ):
            reduction_factor = 1.0 / (average_error + 1)
            transformed_vertices = self.workers.starmap(
                CartogramFeatures.transformVertex,
                zip(
                    self.vertices,
                    itertools.repeat(self._features),
                    itertools.repeat(reduction_factor)
                )
            )

            for feature_id, part, ring, vertex, point in transformed_vertices:
                self[feature_id].vertices[part][ring][vertex] = point

            # invalidate the geometries of all features, so they’re recomputed
            for feature in self:
                del feature._wkt

            iteration += 1
            average_error = self.average_error

    @staticmethod
    def transformVertex(vertex, features, reduction_factor):
        feature_id, part, ring, vertex, point = vertex
        x0, y0 = point

        x = x0
        y = y0

        for feature in features:
            if feature.mass:
                cx = feature.cx
                cy = feature.cy
                distance = math.sqrt((x0 - cx) ** 2 + (y0 - cy) ** 2)

                if distance > feature.radius:
                    # force in points ‘far away’ from the centroid
                    force = feature.mass * feature.radius / distance
                else:
                    # force on points closer to the centroid
                    dr = distance / feature.radius
                    force = feature.mass * (dr ** 2) * (4 - (3 * dr))
                force *= reduction_factor / distance

                x += (x0 - cx) * force
                y += (y0 - cy) * force

        return feature_id, part, ring, vertex, (x, y)


# bloody helper function, TODO: this has to change to something better
def _getattr(obj, name):
    return getattr(obj, name)
