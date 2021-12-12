# -*- coding: utf-8 -*-
"""Main dialog for the cartogram3 plugin."""

# import os

from qgis.core import QgsFieldProxyModel, QgsMapLayerProxyModel
# from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from .cartogram_dialog_ui import Ui_CartogramDialog as FORM_CLASS

# FORM_CLASS, _ = uic.loadUiType(
#     os.path.join(
#         os.path.dirname(__file__),
#         "cartogram_dialog.ui"
#     ),
#     from_imports=True
# )


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

        # connect changed-signal to validation function
        self.fieldListView.selectionModel().selectionChanged.connect(
            self.enable_ok_button_only_when_field_selected
        )

        # sync fieldListView with layerComboBox
        self.layerComboBox.layerChanged.emit(
            self.layerComboBox.currentLayer()
        )

    def enable_ok_button_only_when_field_selected(self, *args, **kwargs):
        """Enable OK button only when at least one field is selected."""
        if self.fieldListView.selectedFields():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
