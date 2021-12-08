# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CartogramDialog
                                 A QGIS plugin
 Generate anamorphic maps
                             -------------------
        begin                : 2017-02-09
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Christoph Fink
        email                : morph@austromorph.space
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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        "cartogram_dialog.ui"
    ),
    from_imports=True
)


class CartogramDialog(QtWidgets.QDialog, FORM_CLASS):
    """Main dialog for the cartogram3 plugin."""

    def __init__(self, parent=None):
        """Initialise a CartogramDialog."""
        super(CartogramDialog, self).__init__(parent)
        self.setupUi(self)
