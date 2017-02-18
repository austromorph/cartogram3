# -*- coding: utf-8 -*-
"""
/***************************************************************************
    QgsFieldListView.py
    -------------------

    Implements a PyQt5 widget, analogue to QgsFieldComboBox
    -------------------
    date        : 2017-02-14
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
    pyqtSlot,
    QItemSelection
)
from PyQt5.QtWidgets import (
    QListView
)
from qgis.gui import (
    QgsFieldModel,
    QgsFieldProxyModel
)


class QgsFieldListView(QListView):
    def __init__(self, parent):
        QListView.__init__(self, parent)

        self.mFieldProxyModel = QgsFieldProxyModel(self)
        self.setModel(self.mFieldProxyModel)

        self.activated.connect(self.indexChanged)

    fieldChanged = pyqtSignal(str)

    def setFilters(self, filters):
        self.mFieldProxyModel.setFilters(filters)

    def setAllowEmptyFieldName(self, allowEmpty=True):
        self.mFieldProxyModel.sourceFieldModel().setAllowEmptyFieldName(
            allowEmpty
        )

    def allowEmptyFieldName(self):
        return self.mFieldProxyModel.sourceFieldModel().allowEmptyFieldName()

    @pyqtSlot("QgsMapLayer*")
    def setLayer(self, layer):
        self.mFieldProxyModel.sourceFieldModel().setLayer(layer)
        self.selectionModel().clearSelection()
        self.selectionModel().selectionChanged.emit(
            QItemSelection(),
            self.selectionModel().selection()
        )

    def layer(self):
        return self.mFieldProxyModel.sourceFieldModel().layer()

    def setField(self, fieldName):
        idx = self.mFieldProxyModel.sourceFieldModel().indexFromName(fieldName)
        if idx.isValid():
            proxyIdx = self.mFieldProxyModel.mapFromSource(idx)
            if proxyIdx.isValid():
                self.setCurrentIndex(idx.row())
                self.fieldChanged.emit(self.currentField())
                return
        self.setCurrentIndex(-1)

    def fieldNameForIndex(self, proxyIndex):
        if not proxyIndex.isValid():
            return ""
        name = self.mFieldProxyModel.data(
            proxyIndex,
            QgsFieldModel.FieldNameRole
        )
        return name

    def currentField(self):
        idx = self.currentIndex()
        proxyIndex = self.mFieldProxyModel.index(idx, 0)
        return self.fieldNameForIndex(proxyIndex)

    def selectedFields(self):
        selectedFields = []
        for proxyIndex in self.selectedIndexes():
            fieldName = self.fieldNameForIndex(proxyIndex)
            if fieldName != "":
                selectedFields.append(fieldName)
        return selectedFields

    @pyqtSlot("QModelIndex")
    def indexChanged(self, idx):
        self.fieldChanged.emit(
            self.fieldNameForIndex(idx)
        )
