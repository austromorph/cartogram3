#!/usr/bin/env python3


"""Provide a cartogram algorithm to the processing toolbox."""

import pathlib

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .cartogramprocessingalgorithm import CartogramProcessingAlgorithm


class CartogramProcessingProvider(QgsProcessingProvider):
    """Provide a cartogram algorithm to the processing toolbox."""

    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(CartogramProcessingAlgorithm())

    def id(self, *args, **kwargs):
        return "cartogram3"

    def name(self, *args, **kwargs):
        return self.tr("Cartogram")

    def icon(self):
        icon_path = pathlib.Path(__file__).parent.parent / "img" / "icon.png"
        return QIcon(f"{icon_path}")
