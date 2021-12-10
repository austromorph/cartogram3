# -*- coding: utf-8 -*-


"""Distort a polygon map so that its area represent a field value."""


import os.path

from .lib import CartogramUserInterfaceMixIn, CartogramWorkOrchestratorMixIn


class Cartogram(CartogramUserInterfaceMixIn, CartogramWorkOrchestratorMixIn):
    """Distort a polygon map so that its area represent a field value."""

    PLUGIN_NAME = "cartogram3"

    def __init__(self, iface):
        """
        Distort a polygon map so that its area represent a field value.

        Arguments
        ---------
        iface : qgis.core.QgsInterface
            An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        super(Cartogram, self).__init__()

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        self.remove_actions()
        self.remove_processing_provider()
