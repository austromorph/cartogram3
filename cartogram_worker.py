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
import os
import platform
import sys
import traceback

from PyQt5.QtCore import (
    pyqtSignal,
    QObject
)

from qgis.core import (
    QgsGeometry,
    QgsMessageLog,
    QgsPointV2,
    QgsVertexId,
    QgsWkbTypes
)

if platform.system() == "Windows":
    sys.argv = [os.path.abspath(__file__)]
    multiprocessing.set_executable(
        os.path.join(sys.exec_prefix, "pythonw.exe")
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

        # remember whether we deal with a MultiGeometry:
        self.isMulti = QgsWkbTypes.isMultiType(layer.dataProvider().wkbType())

        # find the min value > 0 and set all
        # values <= 0 to 1/100 of it
        # (algorithm cannot deal with 0-values
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
        #_metafeat

        # mp.map!!!
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
        inQueue  = multiprocessing.Queue()
        outQueue = multiprocessing.Queue()

        threads = []
        numThreads = multiprocessing.cpu_count() + 1

        for _ in range(numThreads):
            p = multiprocessing.Process(
                target=transformPoint,
                args=(
                    self.metaFeatures,
                    self.reductionFactor,
                    inQueue,
                    outQueue
                )
            )
            p.start()
            threads.append(p)

        features = \
            {feature.id(): feature.geometry()
                for feature in self.layer.getFeatures()}

        for featureId in features:
            abstractGeometry = features[featureId].geometry()
            for p in range(abstractGeometry.partCount()):
                for r in range(abstractGeometry.ringCount(p)):
                    for v in range(abstractGeometry.vertexCount(p, r) - 1):
                        # -1 because the last one is the first one again
                        vertexId = \
                            QgsVertexId(p, r, v, QgsVertexId.SegmentVertex)
                        if not vertexId.isValid():
                            vertexId = QgsVertexId(
                                p, r, v, QgsVertexId.CurveVertex
                            )
                            if not vertexId.isValid():
                                continue
                        point = abstractGeometry.vertexAt(vertexId)
                        inQueue.put(
                            ((featureId, p, r, v), (point.x(), point.y()))
                        )

        for _ in range(numThreads):
            inQueue.put((None, (None, None)))

        while True:
            if self.stopped:
                # clean inQueue
                while True:
                    (f, g) = inQueue.get()
                    if f is None:
                        break

                # put some more death pills so everybody gets one
                for i in range(numThreads):
                    inQueue.put((None, None))

                # wait for the children to die
                for p in threads:
                    p.join()

                # give up ourselves (main thread)
                break

            ((featureId, p, r, v), (x, y)) = outQueue.get()
            if featureId is None:
                numThreads -= 1
                if numThreads == 0:
                    break
                else:
                    continue

            abstractGeometry = features[featureId].geometry().clone()
            abstractGeometry.moveVertex(
                QgsVertexId(p, r, v, QgsVertexId.SegmentVertex),
                QgsPointV2(x, y)
            )
            features[featureId].setGeometry(abstractGeometry)

            self.progress.emit(1)

        self.layer.dataProvider().changeGeometryValues(features)
        self.layer.reload()


def transformPoint(metaFeatures, reductionFactor, inQueue, outQueue):
        while True:
            (vertexId, (x0, y0)) = inQueue.get()
            if vertexId is None:
                outQueue.put(
                    ((None, None, None, None), (None, None))
                )
                return

            x = x0
            y = y0

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

            outQueue.put((vertexId, (x, y)))


class CartogramMetaFeature(object):
    def __init__(self, geometry, value, minValue):

        self.area = geometry.area()
        self.radius = math.sqrt(self.area / math.pi) if self.area > 0 else 0

        if value > 0:
            self.value = value
        else:
            self.value = minValue

        centroid = geometry.centroid().asPoint()
        (self.cx, self.cy) = (centroid.x(), centroid.y())
