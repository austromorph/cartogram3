# -*- coding: utf-8 -*-
"""Main dialog for the cartogram3 plugin."""

# import os

from qgis.core import QgsFieldProxyModel, QgsMapLayerProxyModel
from qgis.PyQt import QtWidgets

from .cartogram_dialog_ui import Ui_CartogramDialog as FORM_CLASS


class CartogramDialog(QtWidgets.QDialog, FORM_CLASS):
    """Main dialog for the cartogram3 plugin."""

    def __init__(self, parent=None):
        """Initialise a CartogramDialog."""
        super().__init__(parent)
        self.setupUi(self)

        # filter ui: polygon layers, numeric fields only
        self.layerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer
        )
        self.fieldListView.setFilters(
            QgsFieldProxyModel.Numeric
        )

        # sync fieldListView with layerComboBox
        self.layerComboBox.layerChanged.emit(
            self.layerComboBox.currentLayer()
        )
