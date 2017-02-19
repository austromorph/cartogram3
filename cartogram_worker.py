# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cartogram Worker

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import math
import multiprocessing
import re
import traceback

from PyQt5.QtCore import (
    pyqtSignal,
    QObject
)

from qgis.core import (
    QgsGeometry,
    QgsMessageLog
)


class CartogramWorker(QObject):
    finished = pyqtSignal(object, str, int, float)
    error = pyqtSignal(Exception, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)

    def __init__(self, layer, fieldName, maxIterations, maxAverageError, tr):
        QObject.__init__(self)

        self.layer = layer
        self.fieldName = fieldName
        self.maxIterations = maxIterations
        self.maxAverageError = maxAverageError
        self.tr = tr

        self.minValue = min([
            feature[fieldName]
            for feature in layer.getFeatures()
            if feature[fieldName] > 0
        ]) / 100.0
        self.numFeatures = self.layer.featureCount()

        self.stopped = False

    def run(self):
        try:
            self.stopped = False

            for feature in self.layer.getFeatures():
                if feature[self.fieldName] <= 0:
                    feature[self.fieldName] = self.minValue

            iterations = 0
            while True:
                # did the user click the cancel button?
                if self.stopped:
                    self.finished.emit(None, "", 0, 0.0)
                    break

                (self.metaFeatures, self.reductionFactor, averageError) = \
                    self.getReductionFactor()

                # stop conditions met?
                if (iterations >= self.maxIterations or
                        averageError <= self.maxAverageError):
                    # return the layer
                    self.finished.emit(
                        self.layer,
                        self.fieldName,
                        iterations,
                        averageError
                    )
                    # also, fast-forward the progress bar
                    # in case we skipped iterations
                    self.progress.emit(
                            self.numFeatures *
                            (self.maxIterations - iterations)
                    )
                    # and finally, break out of the loop
                    break

                # we got until here? well then let’s take this baby
                # for another round
                iterations += 1

                self.status.emit(
                    self.tr("Iteration {i}/{mI} for field ‘{fN}’").format(
                        i=iterations,
                        mI=self.maxIterations,
                        fN=self.fieldName
                    )
                )

                self.transformFeatures()

        except Exception as e:
            self.error.emit(
                e,
                traceback.format_exc()
            )

    def getReductionFactor(self):
        metaFeatures = [
            CartogramMetaFeature(
                QgsGeometry(feature.geometry()),
                feature[self.fieldName],
                self.minValue
            ) for feature in self.layer.getFeatures()]
        totalArea = sum([metaFeature.area for metaFeature in metaFeatures])
        totalValue = sum([metaFeature.value for metaFeature in metaFeatures])

        areaValueRatio = totalArea / totalValue

        totalError = sum([
            self.metaFeatureError(metaFeature, areaValueRatio)
            for metaFeature in metaFeatures
        ])
        averageError = totalError / self.numFeatures
        reductionFactor = 1 / (averageError + 1)

        return (metaFeatures, reductionFactor, averageError)

    def metaFeatureError(self, metaFeature, areaValueRatio):
        desiredArea = metaFeature.value * areaValueRatio
        if desiredArea <= 0:
            metaFeature.mass = 0.0
        else:
            metaFeature.mass = \
                math.sqrt(desiredArea / math.pi) - metaFeature.radius

        metaFeature.sizeError = \
            max(metaFeature.area, desiredArea) / \
            min(metaFeature.area, desiredArea)

        return metaFeature.sizeError

    def transformFeatures(self):
        numThreads = multiprocessing.cpu_count() + 1
        inQueue = multiprocessing.Queue()
        outQueue = multiprocessing.Queue()

        for feature in self.layer.getFeatures():
            inQueue.put((feature.id(), feature.geometry().exportToWkt()), True)
            #QgsMessageLog.logMessage(feature.geometry().exportToWkt())

        for i in range(numThreads):
            inQueue.put((None, None))

        threads = []
        for i in range(numThreads):
            p = multiprocessing.Process(
                target=self.transformFeature,
                args=(inQueue, outQueue)
            )
            p.start()
            threads.append(p)

        while True:
            if self.stopped:
                # clear inQueue
                while True:
                    (featureId, geometry) = inQueue.get(True)
                    if featureId is None:
                        break

                # put some more death pills so everybody gets one
                for i in range(numThreads):
                    inQueue.put((None, None))

                # wait for the children to die
                for p in threads:
                    p.join()

                # give up ourselves (main thread)
                break

            (featureId, geometry) = outQueue.get(True)
            if featureId is None:
                numThreads -= 1
                if numThreads == 0:
                    break
                else:
                    continue

            #QgsMessageLog.logMessage(geometry)

            self.layer.dataProvider().changeGeometryValues({
                featureId: QgsGeometry().fromWkt(geometry)
            })
            self.progress.emit(1)
        self.layer.reload()

    def transformFeature(self, inQueue, outQueue):
        while True:
            (featureId, geometry) = inQueue.get(True)
            if featureId is None:
                outQueue.put((None, None))
                break

            #geometry = QgsGeometry().fromWkt(geometry)

            #if geometry.isMultipart():
            #    geometry = QgsGeometry().fromMultiPolygon([
            #        self.transformPolygon(polygon)
            #        for polygon in geometry.asMultiPolygon()
            #    ])
            #else:
            #    geometry = QgsGeometry().fromPolygon(
            #        self.transformPolygon(
            #            geometry.asPolygon()
            #        )
            #    )

            # parse wkt directly:
            # a) might be faster (no conversions, Queue requires easy format)
            # b) not affected by http://hub.qgis.org/issues/16198

            # for the sake of performance we assume that
            # QgsGeometry.exportToWkt() returns 
            # well-formed WKT strings

            geometryType = geometry[:geometry.index("(")-1]
            geometry = geometry[len(geometryType)+1:]

            if geometryType == "MultiPolygon":
                polygons = geometry[3:-3].split(")),((")
            else:
                polygons = [geometry[3:-3]]

            polygons = ")),((".join(
                self.transformPolygon(polygon) for polygon in polygons
            )

            geometry = \
                "{geometryType} ((({polygons})))".format(
                    geometryType=geometryType,
                    polygons=polygons
                )

            outQueue.put((featureId, geometry))

    def transformPolygon(self, polygon):
        lineStrings = polygon.split("),(")
        return "),(".join(self.transformLine(line) for line in lineStrings)

    def transformLine(self, line):
        points = line.split(",")
        return ",".join(self.transformPoint(point) for point in points)

    def transformPoint(self, point):
        metaFeatures = self.metaFeatures
        reductionFactor = self.reductionFactor
 
        (x0, y0) = point.strip().split(" ")

        x = x0 = float(x0)
        y = y0 = float(y0)

        # calculate the influence of all polygons on this point
        for metaFeature in metaFeatures:
            if metaFeature.mass == 0:
                continue

            cx = metaFeature.cx
            cy = metaFeature.cy
            distance = math.sqrt((x0 - cx) ** 2 + (y0 - cy) ** 2)

            if distance > metaFeature.radius:
                # force on points ‘far away’ from the centroid
                force = metaFeature.mass * metaFeature.radius / distance
            else:
                # force on points close to the centroid
                dr = distance / metaFeature.radius
                force = metaFeature.mass * (dr ** 2) * (4 - (3 * dr))

            force *= reductionFactor / distance

            x += (x0 - cx) * force
            y += (y0 - cy) * force

        point = "{} {}".format(x,y)
        return point


class CartogramMetaFeature(object):
    def __init__(self, geometry, value, minValue):

        self.area = geometry.area()
        self.value = value
        self.radius = math.sqrt(self.area / math.pi)

        centroid = geometry.centroid().asPoint()
        (self.cx, self.cy) = (centroid.x(), centroid.y())
