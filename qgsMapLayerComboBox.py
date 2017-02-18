# -*- coding: utf-8 -*-
"""
/***************************************************************************
    qgsMapLayerComboBox.py
    -------------------

    Implements a PyQt5 widget, pyqt-port from qgsmaplayercombobox.cpp
    -------------------
    date        : 2017-02-18
    copyright   : (c) 2017 Christoph Fink
    email:      : morph@austromorph.space
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QComboBox
)
from qgis.core import (
    QgsMapLayerModel,
    QgsMapLayerProxyModel
)


class QgsMapLayerComboBox(QComboBox):
    def __init__(self, parent):
        QComboBox.__init__(self, parent)

        self.mProxyModel = QgsMapLayerProxyModel(self)
        self.setModel(self.mProxyModel)

        self.activated.connect(self.indexChanged)
        self.mProxyModel.rowsInserted.connect(self.rowsChanged)
        self.mProxyModel.rowsRemoved.connect(self.rowsChanged)

    layerChanged = pyqtSignal("QgsMapLayer*")

    def setFilters(self, filters):
            self.mProxyModel.setFilters(filters)

    def setExcludedProviders(self, providers):
        self.mProxyModel.setExcludedProviders(providers)

    def excludedProviders(self):
        return self.mProxyModel.excludedProviders()

    def setAllowEmptyLayer(self, allowEmpty):
        self.mProxyModel.sourceLayerModel().setAllowEmptyLayer(allowEmpty)

    def allowEmptyLayer(self):
        return self.mProxyModel.sourceLayerModel().allowEmptyLayer()

    def setShowCrs(self, showCrs):
        self.mProxyModel.sourceLayerModel().setShowCrs(showCrs)

    def showCrs(self):
        return self.mProxyModel.sourceLayerModel().showCrs()

    def setAdditionalItems(self, items):
        self.mProxyModel.sourceLayerModel().setAdditionalItems(items)

    def addtionalItems(self):
        return self.mProxyModel.sourceLayerModel().additionalItems()

    def setLayer(self, layer):
        if layer is None:
            self.setCurrentIndex(-1)
            return

        idx = self.mProxyModel.sourceLayerModel().indexFromLayer(layer)
        if idx.isValid():
            proxyIdx = self.mProxyModel.mapFromSource(idx)
            if proxyIdx.isValid():
                self.setCurrentIndex(proxyIdx.row())
                self.layerChanged.emit(self.currentLayer())
                return

        self.setCurrentIndex(-1)
        self.layerChanged.emit(self.currentLayer())

    def currentLayer(self):
        return self.layer(self.currentIndex())

    def layer(self, layerIndex):
        proxyIndex = self.mProxyModel.index(layerIndex, 0)
        if proxyIndex.isValid():
            layer = self.mProxyModel.data(
                proxyIndex,
                QgsMapLayerModel.LayerRole
            )
            return layer
        return None

    @pyqtSlot("QModelIndex")
    @pyqtSlot(int)
    def indexChanged(self, i):
        self.layerChanged.emit(self.currentLayer())

    def rowsChanged(self):
        if self.count() == 1:
            self.layerChanged.emit(self.currentLayer())
        elif self.count() == 0:
            self.layerChanged.emit(None)
