# -*- coding: utf-8 -*-


"""Distort a polygon map so that its area represent a field value."""


import functools
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QLabel, QPushButton, QProgressBar
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import Qgis, QgsMapLayer, QgsProject, QgsWkbTypes
from qgis.gui import QgsMessageBarItem

from ..ui import CartogramDialog


class CartogramUserInterfaceMixIn:
    """Distort a polygon map so that its area represent a field value."""

    def __init__(self):
        """Distort a polygon map so that its area represent a field value."""
        super(CartogramUserInterfaceMixIn, self).__init__()
        self.actions = []
        self.init_translations()

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        """
        Add a toolbar icon to the toolbar.

        Arguments
        ---------
        icon_path : str
            Path to the icon for this action.
        text : str
            Text that should be shown in menu items for this action.
        callback : function
            Function to be called when the action is triggered.
        enabled_flag : bool
            Should the action should be enabled? Default: True.
        add_to_menu : bool
            Should the action should be added to the menu? Default: True.
        add_to_toolbar : bool
            Should the action be added to the toolbar? Default: True.
        status_tip : str
            Show in a popup when mouse pointer hovers over the action.
        parent : QWidget
            Parent widget for the new action. Default: None.
        whats_this : str
            Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        Returns
        -------
        QAction: The action that was created. Note that the action is also
            added to self.actions list.
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled)

        if status_tip:
            action.setStatusTip(status_tip)
        if whats_this:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)

        return action

    def add_result_layer_to_map_canvas(self, layer, field):
        layer_style = QDomDocument()
        self.input_layer.exportNamedStyle(layer_style)
        name = self.tr("Cartogram of {:s}, distorted using ‘{:s}’").format(
            self.input_layer.name(),
            field
        )
        layer.importNamedStyle(layer_style)
        layer.setName(name)
        QgsProject.instance().addMapLayer(layer)
        (
            QgsProject.instance()
            .layerTreeRoot()
            .findLayer(self.input_layer)
            .setItemVisibilityChecked(False)
        )

        if self.have_all_tasks_finished():
            try:
                del self._progress_bar
                self.iface.messageBar().popWidget(self._progress_bar_message_bar_item)
            except RuntimeError:  # ‘wrapped C/C++ object has been deleted’
                pass

    def add_sample_dataset_clicked(self, message_bar_item=None):
        try:
            self.iface.messageBar().popWidget(message_bar_item)
        except TypeError:
            pass
        QgsProject.instance().addMapLayer(self.sample_layer())

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.menu = self.tr("&Cartogram")
        self.dialog = CartogramDialog()

        icon_path = os.path.join(self.plugin_dir, "img", "icon.png")

        self.add_action(
            icon_path,
            text=self.tr("Compute cartogram"),
            callback=self.show_dialog,
            parent=self.iface.mainWindow()
        )
        self.add_action(
            None,
            text=self.tr("Add sample dataset"),
            callback=self.add_sample_dataset_clicked,
            add_to_toolbar=False,
            parent=self.iface.mainWindow()
        )

    def init_translations(self):
        userLocale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            "i18n",
            "{:s}_{:s}.qm".format(self.PLUGIN_NAME, userLocale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def offer_to_add_sample_dataset(self):
        """Display an error message in message bar that offers to add a sample dataset."""
        message_bar_item = self.iface.messageBar().createMessage(self.tr("Error"))

        label = QLabel(
            self.tr("You need at least one polygon vector layer to create a cartogram.")
        )
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_bar_item.layout().addWidget(label)

        button = QPushButton(self.tr("Add sample dataset"))
        button.clicked.connect(
            functools.partial(
                self.add_sample_dataset_clicked,
                message_bar_item=message_bar_item
            )
        )
        message_bar_item.layout().addWidget(button)

        self.iface.messageBar().pushWidget(message_bar_item, Qgis.Critical)

    @property
    def progress_bar(self):
        try:
            return self._progress_bar
        except AttributeError:
            message_bar_item = QgsMessageBarItem("")

            label = QLabel(self.tr("Computing cartogram"))
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            message_bar_item.layout().addWidget(label)

            progress_bar = QProgressBar()
            progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            progress_bar.setMaximum(100)
            message_bar_item.layout().addWidget(progress_bar)

            # cancel_button = QPushButton(self.tr("Cancel"))
            # cancel_button.clicked.connect(self.cancel_all_tasks)
            # message_bar_item.layout().addWidget(cancel_button)

            self.iface.messageBar().pushWidget(message_bar_item)
            self._progress_bar_message_bar_item = message_bar_item
            self._progress_bar = progress_bar

            return self._progress_bar

    def project_has_polygon_layers(self):
        """Check whether the user added at least one polygon layer."""
        for layer in QgsProject.instance().mapLayers().values():
            if (
                    layer.type() == QgsMapLayer.VectorLayer
                    and layer.geometryType() == QgsWkbTypes.PolygonGeometry
            ):
                return True
        return False

    def remove_actions(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.menu,
                action
            )
            self.iface.removeToolBarIcon(action)

    def save_input_layer_metadata(self, layer):
        """Remember the style xml of a layer."""
        layer_style = QDomDocument()
        layer.exportNamedStyle(layer_style)
        self.input_layer_style = layer_style

    def show_dialog(self):
        """Show the main dialog of this plugin."""
        if not self.has_active_tasks():
            if self.project_has_polygon_layers():
                self.dialog.show()
                if self.dialog.exec_():
                    input_layer = self.dialog.layerComboBox.currentLayer()
                    selected_fields = self.dialog.fieldListView.selectedFields()
                    max_iterations = self.dialog.iterationsSpinBox.value()
                    max_average_error = self.dialog.averageErrorDoubleSpinBox.value()

                    self.start_tasks(
                        input_layer,
                        selected_fields,
                        max_iterations,
                        max_average_error
                    )
                    # remember, so we can later copy metadata etc.
                    self.input_layer = input_layer
            else:
                self.offer_to_add_sample_dataset()

    def update_progress_bar(self, value):
        try:
            self.progress_bar.setValue(int(value))
        except RuntimeError:  # ‘wrapped C/C++ object has been deleted’
            pass

    def tr(self, message):
        """
        Retrieve the translation for a string using Qt translation API.

        Arguments
        ---------
        message : str
            The text to be translated

        Returns
        -------
        str:
            The translated text
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
