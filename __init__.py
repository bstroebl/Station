# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Station
                                 A QGIS plugin
 Station
                             -------------------
        begin                : 2016-09-08
        copyright            : (C) 2016 Bernhard Stroebl, KIJ/DV
        email                : bernhard.stroebl@jena.de
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
    """Load Station class from file Station.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Station import Station
    return Station(iface)
