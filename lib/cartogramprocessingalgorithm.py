#!/usr/bin/env python3


"""Provide a cartogram algorithm to the processing toolbox."""


from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
)

from .cartogramfeatures import CartogramFeatures


class CartogramProcessingAlgorithm(QgsProcessingAlgorithm):
    """Provide a cartogram algorithm to the processing toolbox."""

    # identifiers for input and output variables (‘magic strings’)
    INPUT = "INPUT"
    FIELD = "FIELD"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    MAX_AVERAGE_ERROR = "MAX_AVERAGE_ERROR"

    ITERATIONS = "ITERATIONS"
    OUTPUT = "OUTPUT"
    RESIDUAL_AVERAGE_ERROR = "RESIDUAL_AVERAGE_ERROR"

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
                self.INPUT,
                self.tr("Input layer"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr("Field"),
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT
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
                self.tr("max. average error (%)"),
                type=QgsProcessingParameterNumber.Double,
                # metadata={"widget_wrapper": {"decimals": 2}},
                minValue=0.1,
                defaultValue=10.0,
                maxValue=100.0
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output layer"),
                type=QgsProcessing.TypeVectorPolygon
            )
        )
        self.addOutput(
            QgsProcessingOutputString(
                self.FIELD,
                self.tr("Field")
            )
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.ITERATIONS,
                self.tr("Iterations needed to meet residual error threshold.")
            )
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.RESIDUAL_AVERAGE_ERROR,
                self.tr("Residual average error.")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        if input_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        field_name = self.parameterAsFields(parameters, self.FIELD, context)[0]
        max_iterations = self.parameterAsInt(parameters, self.MAX_ITERATIONS, context)
        max_average_error = self.parameterAsDouble(parameters, self.MAX_AVERAGE_ERROR, context)
        max_average_error = (max_average_error / 100.0 + 1.0)  # input = percentage

        output_layer, output_layer_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            input_layer.fields(),
            input_layer.wkbType(),
            input_layer.sourceCrs()
        )
        if output_layer is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # first, copy all features to a temporary layer
        # we use a zero-width buffer algorithm to do this,
        # in order to fix potential invalid geometries at the same time
        memory_layer = context.getMapLayer(
            processing.run(
                "native:buffer", {
                    "INPUT": parameters[self.INPUT],
                    "DISTANCE": 0.0,
                    "OUTPUT": "memory:"
                },
                context=context,
                is_child_algorithm=True
            )["OUTPUT"]
        )

        cartogram_features = CartogramFeatures.from_polygon_layer(memory_layer, field_name, feedback)
        iterations, average_error = cartogram_features.transform(
            max_iterations,
            max_average_error
        )
        cartogram_features.copy_geometries_back_to_layer(memory_layer)

        # We are sometimes left with slithers and polygons misshaped in other ways,
        # a zero-buffer around them works well
        buffered_layer = context.getMapLayer(
            processing.run(
                "native:buffer", {
                    "INPUT": memory_layer,
                    "DISTANCE": 0.0,
                    "OUTPUT": "memory:"
                },
                context=context,
                is_child_algorithm=True
            )["OUTPUT"]
        )

        # finally, copy features to the output sink
        for feature in buffered_layer.getFeatures():
            output_layer.addFeature(feature, QgsFeatureSink.FastInsert)

        return {
            self.OUTPUT: output_layer_id,
            self.FIELD: field_name,
            self.ITERATIONS: iterations,
            self.RESIDUAL_AVERAGE_ERROR: (average_error - 1) * 100.0  # we report in %
        }
