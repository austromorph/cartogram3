#!/usr/bin/env python3


"""Handle a list of `CartogramFeature`."""


import functools
import itertools
import math
import multiprocessing
import os.path
import platform
import sys

from qgis.core import QgsGeometry, QgsProcessingFeedback

from .cartogramfeature import CartogramFeature


if platform.system() == "Windows":
    sys.argv = [os.path.abspath(__file__)]
    multiprocessing.set_executable(os.path.join(sys.exec_prefix, "pythonw.exe"))
elif platform.system() == "Darwin":
    sys.argv = [os.path.abspath(__file__)]
    multiprocessing.set_executable(os.path.join(sys.exec_prefix, "bin", "python3"))


class CartogramFeatures:
    """Handle a list of `CartogramFeature`."""
    def __init__(self, feedback=QgsProcessingFeedback()):
        """Handle a list of `CartogramFeature`."""
        self._features = {}
        self.workers = multiprocessing.get_context("spawn").Pool()
        self.feedback = feedback
        self.feedback.canceled.connect(self.stop_workers)

    def __del__(self):
        """Take care of the worker pool upon unloading."""
        self.workers.close()
        del self.workers

    # next two methods not alphabetical order, because they’re
    # instantiator and data output

    @staticmethod
    def from_polygon_layer(layer, field_name, feedback=QgsProcessingFeedback()):
        cartogram_features = CartogramFeatures(feedback)
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

    def copy_geometries_back_to_layer(self, layer):
        # this MUST be the same layer as used for `from_polygon_layer`
        layer.startEditing()
        for feature in self.features:
            layer.changeGeometry(feature.id, QgsGeometry().fromWkt(feature.wkt))
        layer.commitChanges()

    def __setitem__(self, feature_id, cartogram_feature):
        self._features[feature_id] = cartogram_feature

    def __getitem__(self, feature_id):
        return self._features[feature_id]

    def __iter__(self):
        return self.values()

    def __len__(self):
        return len(self._features)

    @property
    def average_error(self):
        return self.total_error / len(self)

    @property
    @functools.cache
    def _chunksize(self):
        """Use this chunksize for multiprocessing.imap() etc..."""
        chunksize = min(
            10000,
            int(
                self.total_number_of_vertices
                / (2 * multiprocessing.cpu_count())
            )
        )
        return chunksize

    @property
    def features(self):
        return self.values()

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

    def stop_workers(self, *args, **kwargs):
        self.workers.terminate()
        self.workers.join()

    @property
    def total_area(self):
        total_area = sum(
            self.workers.imap_unordered(
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
            self.workers.imap_unordered(
                # lambda x: x.sizeerror,
                functools.partial(_getattr, name="sizeerror"),
                self
            )
        )
        return total_error

    @property
    @functools.cache
    def total_number_of_vertices(self):
        return sum(1 for _ in self.vertices)

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
                and not self.feedback.isCanceled()
        ):
            reduction_factor = 1.0 / (average_error + 1)
            transformed_vertices = self.workers.imap_unordered(
                functools.partial(
                    CartogramFeatures.transformVertex,
                    features=list(self.features),
                    reduction_factor=reduction_factor
                ),
                self.vertices,
                chunksize=self._chunksize
            )

            number_of_vertices_processed = 0
            for feature_id, part, ring, vertex, point in transformed_vertices:
                self[feature_id].vertices[part, ring, vertex] = point

                number_of_vertices_processed += 1
                self.feedback.setProgress(
                    (
                        (
                            (iteration * self.total_number_of_vertices)  # completed iterations
                            + number_of_vertices_processed  # current iteration
                        )
                        / (self.total_number_of_vertices * max_iterations)  # expected overall vertex ops
                    )
                    * 100  # percentage
                )

            for feature in self:
                # invalidate the geometry of each feature,
                # to force reconstructing it
                # from the changed set of vertices
                feature.wkt = None

            iteration += 1
            average_error = self.average_error

        return iteration, average_error

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
                    # force on points ‘far away’ from the centroid
                    force = feature.mass * feature.radius / distance
                else:
                    # force on points closer to the centroid
                    dr = distance / feature.radius
                    force = feature.mass * (dr ** 2) * (4 - (3 * dr))
                force *= reduction_factor / distance

                x += (x0 - cx) * force
                y += (y0 - cy) * force

        return feature_id, part, ring, vertex, (x, y)


def _getattr(obj, name):
    return getattr(obj, name)
