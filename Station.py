# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Station
                                 A QGIS plugin
 Station
                              -------------------
        begin                : 2016-09-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Bernhard Stroebl, KIJ/DV
        email                : bernhard.stroebl@jena.de
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QColor, QInputDialog
# Initialize Qt resources from file resources.py
import resources
import os.path
import math
from qgis.core import *
from qgis.gui import *

class Station:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Station_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Station')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Station')
        self.toolbar.setObjectName(u'Station')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Station', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Station/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'determine on line'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Station'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        mapCanvas = self.iface.mapCanvas()
        # Create the appropriate map tool and connect the showStationSlot() signal.
        self.emitPoint = QgsMapToolEmitPoint(mapCanvas)
        mapCanvas.setMapTool(self.emitPoint)
        self.emitPoint.canvasClicked.connect(self.showStationSlot)

    def showStationSlot(self, pnt, but):
        title = u"Show station"
        lineLayer = self.iface.activeLayer()
        
        if lineLayer == None:
            return None
        
        lineLayer.removeSelection()
        step = 0.5
        msg = 'Error'
        self.debug(str(pnt))
        # step 1 choose the line the user clicked on
        while step <= 5:
            llx = pnt.x()-step
            lly = pnt.y()-step
            urx = pnt.x()+step
            ury = pnt.y()+step
            searchRect = QgsRectangle(llx, lly, urx, ury)
            lineLayer.select(searchRect, False)
            numSel = lineLayer.selectedFeatureCount()

            if numSel == 0: # enlarge search distance
                step = step + 0.5
            else:
                break

        fidList = []
        choiceList = []

        if numSel > 1:
            for feat in lineLayer.selectedFeatures():
                fid = feat.id()
                fidList.append(fid)
                choiceList.append("id " + str(fid))

            thisChoice, ok = QInputDialog.getItem(None, title,
                            u"Choose line", choiceList, 0, False)

            if not ok:
                return None

            for i in range(len(choiceList)):

                if choiceList[i] == thisChoice:
                    fid = fidList[i]
                    feature = QgsFeature()
                    lineLayer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).nextFeature(feature)
                    break

        elif numSel == 1:
            feature = lineLayer.selectedFeatures()[0]
        else:
            msg = u'no line selected'

        mapCanvas = None

        # step 2 determine station
        if numSel > 0:
            thisLine = feature.geometry()
            radius = QgsGeometry.fromPoint(pnt).distance(thisLine)
            radius = radius + 0.01
            pointList = []

            #create a "circle" cutting thisLine
            for anAngle in range(360):
                dx = radius * math.cos(math.radians(anAngle))
                dy = radius * math.sin(math.radians(anAngle))
                newX = pnt.x() + dx
                newY = pnt.y() + dy
                pointList.append(QgsPoint(newX, newY))

            cuttingCircle = QgsGeometry.fromPolyline(pointList)
            
            # cut thisLine with cuttingCircle
            partOfLine = thisLine.intersection(cuttingCircle)

            if partOfLine.wkbType() == 4: #MULTIPOINT
                # change into QgsGeometry object
                partOfLine = QgsGeometry.fromMultiPoint(\
                    partOfLine.asMultiPoint()).asGeometryCollection()

                # determine slope of partOfLine using its start and end point
                dx = partOfLine[0].asPoint().x() - partOfLine[1].asPoint().x()
                dy = partOfLine[0].asPoint().y() - partOfLine[1].asPoint().y()
                # calculate perpendicular point by slope * 0.5
                lotX = partOfLine[1].asPoint().x() + (0.5 * dx)
                lotY = partOfLine[1].asPoint().y() + (0.5 * dy)
                perpPoint = QgsPoint(lotX, lotY)
                # Calculate a point on the perpendicular line on the other side of thisLine
                dx2 = pnt.x() - lotX
                dy2 = pnt.y() - lotY
                mirrorPoint = QgsPoint(lotX - dx2, lotY - dy2)


                split = QgsGeometry(thisLine)
                res, geomList, topoList = split.splitGeometry([pnt, mirrorPoint], False)

                if res == 0: # success
                    if thisLine.vertexAt(0) == split.vertexAt(0):
                        station = split.length()
                    else:
                        station = geomList[0].length()

                    # show station point
                    mapCanvas=self.iface.mapCanvas()
                    marker = QgsVertexMarker(mapCanvas)
                    marker.setCenter(perpPoint)
                    marker.setIconType(1)
                    marker.setIconSize(15)
                    selColor = self.getProjectSelectionColor()
                    myColor = QColor(255 - selColor.red(),
                                           255 - selColor.green(),
                                           255 - selColor.blue())
                    marker.setColor(myColor)
                    marker.setPenWidth(1)
                    msg = u"Station: " + str(math.ceil(station))
                else:
                    msg = "no split"

            else:
                msg = "no Multipoint, but " + str(partOfLine.wkbType())

        else:
            msg = "numSel = " + str(numSel)

        if msg != '':
            self.iface.messageBar().pushMessage(title,
                msg, duration = 10)

            if mapCanvas:
                marker.setIconType(0)
                marker.update()
    
    def getProjectSelectionColor(self):
        prj = QgsProject.instance()
        r = prj.readNumEntry("Gui", "/SelectionColorRedPart", 255)[0]
        g = prj.readNumEntry("Gui", "/SelectionColorGreenPart", 255)[0]
        b = prj.readNumEntry("Gui", "/SelectionColorBluePart", 0)[0]
        a = prj.readNumEntry("Gui", "/SelectionColorAlphaPart", 255)[0]
        return QColor(r, g, b ,a)
    
    def debug(self,  msg):
        QgsMessageLog.logMessage(msg)