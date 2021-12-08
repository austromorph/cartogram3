#!/usr/bin/env python3


"""Provide a cartogram algorithm to the processing toolbox."""

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsVectorLayer,
    QgsWkbTypes
)

from .cartogramfeatures import CartogramFeatures


class CartogramProcessingAlgorithm(QgsProcessingAlgorithm):
    """Provide a cartogram algorithm to the processing toolbox."""

    # identifiers for input and output variables (‘magic strings’)
    INPUT_LAYER = "INPUT_LAYER"
    INPUT_LAYER_FIELD = "INPUT_LAYER_FIELD"
    OUTPUT_LAYER = "OUTPUT_LAYER"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    MAX_AVERAGE_ERROR = "MAX_AVERAGE_ERROR"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return CartogramProcessingAlgorithm()

    def name(self):
        return "compute_cartogram"

    def displayName(self):
        return self.tr("Compute cartogram")

    def group(self):
        return self.tr("Vector geometry")

    def groupId(self):
        return "vectorgeometry"

    def shortHelpString(self):
        return self.tr("Compute cartogram")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                self.tr("Input layer"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_LAYER_FIELD,
                self.tr("Field"),
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT_LAYER
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAX_ITERATIONS,
                self.tr("max. number of iterations"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAX_AVERAGE_ERROR,
                self.tr("max. average error"),
                type=QgsProcessingParameterNumber.Double,
                # metadata={"widget_wrapper": {"decimals": 2}},
                minValue=0.001,
                defaultValue=0.1,
                maxValue=1.0
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER,
                self.tr("Output layer"),
                type=QgsProcessing.TypeVectorPolygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        if input_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_LAYER))

        field_name = self.parameterAsFields(parameters, self.INPUT_LAYER_FIELD, context)[0]

        output_layer, output_layer_id = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            input_layer.fields(),
            input_layer.wkbType(),
            input_layer.sourceCrs()
        )
        if output_layer is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT_LAYER))

        # first, copy all features to a temporary layer
        memory_layer = QgsVectorLayer(
            QgsWkbTypes.displayString(input_layer.wkbType())
            + "?crs=" + input_layer.sourceCrs().authid()
            + "&index=yes",
            "cartogram3 working copy",
            "memory"
        )
        memory_layer_data_provider = memory_layer.dataProvider()

        # copy the structure
        memory_layer.startEditing()
        memory_layer_data_provider.addAttributes(
            input_layer.fields().toList()
        )
        memory_layer.commitChanges()

        memory_layer_data_provider.addFeatures(
            list(input_layer.getFeatures())
        )

        cartogram_features = CartogramFeatures.from_polygon_layer(memory_layer, field_name)
        cartogram_features.transform()
        cartogram_features.copy_geometries_back_to_layer()

        # finally, copy features to the output sink
        for feature in memory_layer.getFeatures():
            output_layer.addFeature(feature, QgsFeatureSink.FastInsert)

        return {self.OUTPUT_LAYER: output_layer_id}
