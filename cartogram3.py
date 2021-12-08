# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cartogram
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
import os.path
import locale
import queue
import timeit

from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    qVersion,
    QCoreApplication,
    Qt,
    QThread
)
from qgis.PyQt.QtGui import (
    QIcon
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QProgressBar
)
from qgis.PyQt.QtXml import (
    QDomDocument
)

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsFieldProxyModel,
    QgsMapLayer,
    QgsMapLayerProxyModel,
    QgsMessageLog,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes
)

from .cartogramprocessingprovider import CartogramProcessingProvider
from .ui import CartogramDialog
from .workers import CartogramWorker


class Cartogram:
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
        userLocale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'cartogram3_{}.qm'.format(userLocale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        try:
            locale.setlocale(
                locale.LC_ALL,
                QSettings().value('locale/userLocale')
            )
        except:  # noqa: E722
            pass

        # Create the dialog (after translation) and keep reference
        self.dialog = CartogramDialog()

        # filter ui: polygon layers, numeric fields only
        self.dialog.layerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer
        )
        self.dialog.fieldListView.setFilters(
            QgsFieldProxyModel.Numeric
        )

        # connect changed-signal to validation function
        self.dialog.fieldListView.selectionModel().selectionChanged.connect(
            self.validateInputs
        )

        self.actions = []
        self.menu = self.tr("&Cartogram")

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
        return QCoreApplication.translate('Cartogram', message)

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
        parent=None
    ):
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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.toolbar = self.iface.addToolBar("Compute cartogram")
        self.toolbar.setObjectName("Cartogram")

        icon_path = os.path.join(self.plugin_dir, "img", "icon.png")
        self.add_action(
            icon_path,
            text=self.tr("Compute cartogram"),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.add_action(
            None,
            text=self.tr("Add sample dataset"),
            callback=self.addSampleDataset,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        self.initProcessing()

    def initProcessing(self):
        self.provider = CartogramProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def validateInputs(self, unusedArgumentToMatchQtSignal=0):
        try:
            workersRunning = not self.jobs.empty()
        except:  # noqa: E722
            workersRunning = False
        if (
                workersRunning
                or len(self.dialog.fieldListView.selectedFields()) < 1
        ):
            self.dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def run(self):
        """Run method that performs all the real work"""

        # check whether we have at least once polygon vector layer
        if [
                name for name, layer in QgsProject.instance().mapLayers().items()
                if (
                    layer.type() == QgsMapLayer.VectorLayer
                    and layer.geometryType() == QgsWkbTypes.PolygonGeometry
                )
        ]:
            # otherwise display an error message and offer to add
            # a sample dataset
            errorMessageLabel = QLabel(
                self.tr(
                    "You need at least one polygon vector layer "
                    + "to create a cartogram."
                )
            )
            errorMessageLabel.setAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )
            addSampleDatasetButton = QPushButton(
                self.tr("Add sample dataset")
            )
            addSampleDatasetButton.clicked.connect(
                self.addSampleDataset
            )

            self.messageBarItem = self.iface.messageBar().createMessage(
                self.tr("Error")
            )
            for widget in [
                errorMessageLabel,
                addSampleDatasetButton
            ]:
                self.messageBarItem.layout().addWidget(widget)

            self.iface.messageBar().pushWidget(
                self.messageBarItem,
                Qgis.Critical
            )
            return False

        # sync fieldListView with layerComboBox
        self.dialog.layerComboBox.layerChanged.emit(
            self.dialog.layerComboBox.currentLayer()
        )

        # show the dialog
        self.dialog.show()
        self.validateInputs()

        # Run the dialog event loop
        result = self.dialog.exec_()
        # See if OK was pressed
        if result:
            self.t = timeit.default_timer()

            self.inputLayer = self.dialog.layerComboBox.currentLayer()
            self.selectedFields = self.dialog.fieldListView.selectedFields()
            self.maxIterations = self.dialog.iterationsSpinBox.value()
            self.maxAverageError = \
                self.dialog.averageErrorDoubleSpinBox.value() / 100.0 + 1.0

            # remember the input layer’s style
            self.inputLayerStyle = QDomDocument()
            # QgsMapLayer.exportNamedStyle() changed its signature
            # between QGIS 3.2 and 3.4, for now, support both
            try:
                # >=3.4
                self.inputLayer.exportNamedStyle(self.inputLayerStyle)
            except TypeError:
                # <=3.2
                self.inputLayer.exportNamedStyle(self.inputLayerStyle, None)

            # set up all widgets for status reporting
            self.progressBar = QProgressBar()
            self.progressBar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.progressBar.setMaximum(
                len(self.selectedFields)
                * self.maxIterations
                * len(list(self.inputLayer.getFeatures()))
                + 1
            )

            self.statusMessageLabel = QLabel("")
            self.statusMessageLabel.setAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )

            cancelButton = QPushButton(self.tr("Cancel"))
            cancelButton.clicked.connect(self.stopWorker)

            self.messageBarItem = self.iface.messageBar().createMessage("")
            for widget in [
                self.statusMessageLabel,
                self.progressBar,
                cancelButton
            ]:
                self.messageBarItem.layout().addWidget(widget)

            self.iface.messageBar().pushWidget(
                self.messageBarItem,
                Qgis.Info
            )

            self.updateProgressBar()
            self.updateStatusMessage("starting")

            self.startWorker()

    def updateStatusMessage(self, message=""):
        try:
            self.statusMessageLabel.setText("cartogram3: " + message)
        except:  # noqa: E722
            pass

    def updateProgressBar(self, increase=1):
        try:
            self.progressBar.setValue(
                self.progressBar.value() + increase
            )
        except:  # noqa: E722
            pass

    def startWorker(self):
        worker = CartogramWorker(
            self.inputLayer,
            self.selectedFields,
            self.maxIterations,
            self.maxAverageError,
            self.tr
        )
        thread = QThread()
        worker.moveToThread(thread)

        # connecting signals+slots
        worker.finished.connect(self.workerFinished)
        worker.cartogramComplete.connect(self.workerCartogramComplete)
        worker.error.connect(self.workerError)
        worker.progress.connect(self.updateProgressBar)
        worker.status.connect(self.updateStatusMessage)

        thread.started.connect(worker.run)
        thread.start()

        self.worker = worker
        self.thread = thread

    def stopWorker(self):
        self.worker.stopped = True

    def workerFinished(self):
        try:
            self.worker.deleteLater()
        except:  # noqa: E722
            pass
        self.thread.quit()
        self.thread.wait()
        self.thread.terminate()
        self.thread.deleteLater()

        self.iface.messageBar().popWidget(self.messageBarItem)
        self.t = timeit.default_timer() - self.t

    def workerCartogramComplete(
        self,
        layer=None,
        fieldName=None,
        iterations=None,
        avgError=None
    ):
        if layer is not None:
            # try to update the style xml before applying it
            # (QgsMapLayer.exportNamedStyle() changed its signature
            # between QGIS 3.2 and 3.4, for now, support both)
            try:
                # >=3.4
                self.inputLayer.exportNamedStyle(self.inputLayerStyle)
            except TypeError:
                # <=3.2
                self.inputLayer.exportNamedStyle(self.inputLayerStyle, None)
            layer.importNamedStyle(self.inputLayerStyle)

            # hide input layer
            try:
                QgsProject.instance().layerTreeRoot() \
                    .findLayer(self.inputLayer) \
                    .setItemVisibilityChecked(False)
            except Exception as e:
                QgsMessageLog.logMessage(
                    repr(e),
                    "Plugins",
                    Qgis.Warning
                )

            # add the layer to the project
            QgsProject.instance().addMapLayer(layer)

            avgError -= 1
            QgsMessageLog.logMessage(
                self.tr(
                    "cartogram3 successfully finished computing a "
                    + "cartogram for field ‘{fieldName}’ after "
                    + "{iterations} iterations with {avgError:.2n}% "
                    + "average error remaining."
                ).format(
                    iterations=iterations,
                    avgError=(avgError * 100),
                    fieldName=fieldName
                ),
                "Plugins",
                Qgis.Info
            )
        else:
            QgsMessageLog.logMessage(
                self.tr("cartogram3 computation cancelled by user")
            ),
            "Plugins",
            Qgis.Info

    def workerError(self, e, exceptionString):
        self.iface.messageBar().pushCritical(
            self.tr("Error"),
            self.tr(
                "An error occurred during cartogram creation. "
                + "Please see the “Plugins” section of the message "
                + "log for details."
            )
        )
        QgsMessageLog.logMessage(
            exceptionString,
            "Plugins",
            Qgis.Critical
        )

        # empty the job queue
        self.jobs = queue.Queue()
        self.workerFinished()

    def addSampleDataset(self):
        try:
            self.iface.messageBar().popWidget(
                self.messageBarItem
            )
        except:  # noqa: E722
            pass

        sampleDataset = QgsVectorLayer(
            os.path.join(
                self.plugin_dir,
                "data",
                "Austria_PopulationByNUTS2.gml"
            ),
            ""
        )

        sampleLayer = self.createMemoryLayer(
            "Austria_Population_NUTS2_20170101",
            sampleDataset
        )

        sampleLayer.loadNamedStyle(
            os.path.join(
                self.plugin_dir,
                "data",
                "Austria_PopulationByNUTS2.qml"
            )
        )

        sampleLayer.setTitle("Austria: Population by NUTS2 regions, 1 Jan 2017")
        sampleLayer.setShortName("Austria_Population_NUTS2_20170101")
        sampleLayer.setAbstract(
            "Austria’s population by NUTS2 region, as of 1 Jan 2017 \n"
            + "\n"
            + "Data sources: \n"
            + "    http://ec.europa.eu/eurostat/web/gisco/geodata/"
            + "reference-data/administrative-units-statistical-units/"
            + "nuts#nuts13 \n"
            + "    http://www.statistik.at/web_de/statistiken/"
            + "menschen_und_gesellschaft/bevoelkerung/"
            + "bevoelkerungsstand_und_veraenderung/"
            + "bevoelkerung_zu_jahres-_quartalsanfang/index.html"
        )

        QgsProject.instance().addMapLayer(sampleLayer)
        del sampleDataset

    def createMemoryLayer(self, layerName, sourceLayer):
        # create empty memory layer
        memoryLayer = QgsVectorLayer(
            QgsWkbTypes.geometryDisplayString(sourceLayer.geometryType())
            + "?crs=" + sourceLayer.crs().authid()
            + "&index=yes",
            layerName,
            "memory"
        )
        memoryLayerDataProvider = memoryLayer.dataProvider()

        # copy the table structure
        memoryLayerDataProvider.addAttributes(
            sourceLayer.fields().toList()
        )
        memoryLayer.updateFields()

        # copy the features
        memoryLayerDataProvider.addFeatures(
            list(sourceLayer.getFeatures())
        )

        return memoryLayer
