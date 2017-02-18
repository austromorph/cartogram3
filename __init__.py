# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cartogram
                                 A QGIS plugin
 Generate anamorphic maps
                             -------------------
        begin                : 2017-02-09
        copyright            : (C) 2017 by Christoph Fink
        email                : morph@austromorph.space
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Cartogram class from file Cartogram.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .cartogram import Cartogram
    return Cartogram(iface)
