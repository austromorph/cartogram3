# -*- coding: utf-8 -*-


"""Distort a polygon map so that its area represent a field value."""


import os.path

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsVectorLayer,
    QgsWkbTypes
)

from . import CartogramProcessingProvider


class CartogramWorkOrchestratorMixIn:
    """Manage the tasks of the plugin’s workers."""
    def __init__(self):
        """Manage the tasks of the plugin’s workers."""
        super(CartogramWorkOrchestratorMixIn, self).__init__()
        self.add_processing_provider()
        self.tasks = []
        self.context = QgsProcessingContext()
        self.feedback = QgsProcessingFeedback()

    def add_processing_provider(self):
        self.provider = CartogramProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def cancel_all_tasks(self):
        self.disable_cancel_button()
        for task in self.tasks:
            task.cancel()

    def has_active_tasks(self):
        for task in self.tasks:
            if task.isActive():
                return True
        return False

    def have_all_tasks_finished(self):
        return not self.has_active_tasks()

    def remove_processing_provider(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def sample_layer(self):
        source_layer = QgsVectorLayer(
            os.path.join(self.plugin_dir, "data", "Austria_PopulationByNUTS2.gml"),
            ""
        )

        # (empty) memory layer
        sample_layer = QgsVectorLayer(
            QgsWkbTypes.geometryDisplayString(source_layer.geometryType())
            + "?crs=" + source_layer.crs().authid()
            + "&index=yes",
            "Austria_Population_NUTS2_20170101",
            "memory"
        )
        sample_layer_data_provider = sample_layer.dataProvider()
        sample_layer_data_provider.addAttributes(source_layer.fields().toList())
        sample_layer.updateFields()
        sample_layer_data_provider.addFeatures(list(source_layer.getFeatures()))

        sample_layer.loadNamedStyle(
            os.path.join(self.plugin_dir, "data", "Austria_PopulationByNUTS2.qml")
        )

        sample_layer.setTitle("Austria: Population by NUTS2 regions, 1 Jan 2017")
        sample_layer.setShortName("Austria_Population_NUTS2_20170101")
        sample_layer.setAbstract(
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

        return sample_layer

    def start_task(self, input_layer, field, max_iterations, max_average_error):
        task = QgsProcessingAlgRunnerTask(
            QgsApplication.processingRegistry().algorithmById("cartogram3:compute_cartogram"),
            {
                "INPUT": input_layer,
                "FIELD": field,
                "MAX_ITERATIONS": max_iterations,
                "MAX_AVERAGE_ERROR": max_average_error,
                "OUTPUT": "memory:"
            },
            self.context,
            self.feedback
        )
        task.executed.connect(self.task_finished)
        task.progressChanged.connect(self.update_progress)
        QgsApplication.taskManager().addTask(task)
        return task  # , context, feedback

    def start_tasks(self, input_layer, fields, max_iterations, max_average_error):
        # create a fresh feedback and context (so we don’t stay in isCanceled(), for instance)
        self.context = QgsProcessingContext()
        self.feedback = QgsProcessingFeedback()
        for field in fields:
            self.tasks.append(self.start_task(input_layer, field, max_iterations, max_average_error))

    def task_finished(self, successful, results={}):
        if successful:
            output_layer = self.context.getMapLayer(results["OUTPUT"])
            if output_layer and output_layer.isValid():
                layer = self.context.takeResultLayer(output_layer.id())
                self.add_result_layer_to_map_canvas(layer, results["FIELD"])
        else:
            if self.feedback.isCanceled():
                self.feedback.pushWarning("User canceled cartogram computation")
            self.feedback.reportError("Failed to compute cartogram")

        if self.have_all_tasks_finished():
            self.tasks = []

        self.clean_up_ui()  # remove progress bar

    def update_progress(self, *args, **kwargs):
        progress = sum([task.progress() for task in self.tasks]) / len(self.tasks)
        self.update_progress_bar(progress)
