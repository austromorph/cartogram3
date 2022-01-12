<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es">
<context>
    <name>Cartogram</name>
    <message>
        <location filename="../cartogram3.py" line="112"/>
        <source>&amp;cartogram3</source>
        <translation type="obsolete">&amp;Cartograma</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="209"/>
        <source>Compute cartogram</source>
        <translation type="obsolete">Preparar cartograma</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="111"/>
        <source>&amp;Cartogram</source>
        <translation type="obsolete">&amp;Cartograma</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="485"/>
        <source>Error</source>
        <translation type="obsolete">Error</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="279"/>
        <source>You need at least one polygon vector layer to create a cartogram.</source>
        <translation type="obsolete">Para preparar un cartograma se necesita al menos una capa vectorial de polígonos.</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="357"/>
        <source>Cancel</source>
        <translation type="obsolete">Cancelar</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="466"/>
        <source>cartogram3 successfully finished computing a cartogram for field ‘{fieldName}’ after {iterations} iterations with {avgError:.2n}% average error remaining.</source>
        <translation type="obsolete">cartogram3: Se terminó con exito la computación de un cartograma por el atributo «{fieldName}». Después {iterations} iteraciónes se queda un error promedio de {avgError:.2n}%.</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="477"/>
        <source>cartogram3 computation cancelled by user</source>
        <translation type="obsolete">cartogram3: computación cancelada por usario</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="485"/>
        <source>An error occurred during cartogram creation. Please see the ‘Plugins’ section of the message log for details.</source>
        <translation type="obsolete">Ocurrió un error al ejecutar la computación.</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="286"/>
        <source>Add sample dataset</source>
        <translation type="obsolete">Añadir datos de muestra</translation>
    </message>
</context>
<context>
    <name>CartogramDialog</name>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="14"/>
        <source>cartogram3</source>
        <translation>cartogram3</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="20"/>
        <source>Input layer:</source>
        <translation>Capa de entrada:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="27"/>
        <source>Field(s):</source>
        <translation type="obsolete">Atributo(s):</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="47"/>
        <source>Stop conditions:</source>
        <translation>Metas:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="63"/>
        <source>max. number of iterations:</source>
        <translation>max. iteraciones:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="83"/>
        <source>max. average error:</source>
        <translation>error promedio max.:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="90"/>
        <source>%</source>
        <translation>%</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="103"/>
        <source>Calculation stops as soon as one condition is met.</source>
        <translation>La computación se termina tan pronto como se satisfaga por lo menos una de las condiciones.</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="30"/>
        <source>To compute cartograms for multiple fields, please use the Processing toolbox batch functionality.</source>
        <translation>Para calcular cartogramas para más que un campo, por favor utilice la funcionalidad de lotes de la caja de herramientas de Proceso.</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="33"/>
        <source>Field:</source>
        <translation>Campo</translation>
    </message>
</context>
<context>
    <name>CartogramProcessingAlgorithm</name>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="59"/>
        <source>Compute cartogram</source>
        <translation>Preparar cartograma</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="53"/>
        <source>Vector geometry</source>
        <translation>Geometría vectorial</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="62"/>
        <source>Input layer</source>
        <translation>Capa de entrada</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="103"/>
        <source>Field</source>
        <translation>Campo</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="77"/>
        <source>max. number of iterations</source>
        <translation>max. iteraciones</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="85"/>
        <source>max. average error (%)</source>
        <translation>error promedio max.</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="96"/>
        <source>Output layer</source>
        <translation>Capa alineada</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="109"/>
        <source>Iterations needed to meet residual error threshold.</source>
        <translation>Iteraciones que eran necesarias para alcanzar al deseado error residual</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="115"/>
        <source>Residual average error.</source>
        <translation>promedia error residual</translation>
    </message>
</context>
<context>
    <name>CartogramProcessingProvider</name>
    <message>
        <location filename="../lib/cartogramprocessingprovider.py" line="25"/>
        <source>Cartogram</source>
        <translation>Cartograma</translation>
    </message>
</context>
<context>
    <name>CartogramUserInterfaceMixIn</name>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="94"/>
        <source>Cartogram of {:s}, distorted using ‘{:s}’</source>
        <translation>Cartograma de «{:s}», distorsionada por el campo «{:s}»</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="126"/>
        <source>Cancelled</source>
        <translation>Cancelado</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="151"/>
        <source>&amp;Cartogram</source>
        <translation>&amp;Cartograma</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="156"/>
        <source>Compute cartogram</source>
        <translation>Preparar cartograma</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="193"/>
        <source>Add sample dataset</source>
        <translation>Añadir datos de muestra</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="185"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="187"/>
        <source>You need at least one polygon vector layer to create a cartogram.</source>
        <translation>Para preparar un cartograma se necesita al menos una capa vectorial de polígonos.</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="211"/>
        <source>Computing cartogram</source>
        <translation>Preparando cartograma</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="220"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="133"/>
        <source>Geographic CRS</source>
        <translation>Sistema de referencia de coordenadas geográficas</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="133"/>
        <source>Computing a cartogram for a layer with a geographic CRS might not yield best results (consider reprojecting the layer to a projected coordinate system). 

Do you want to proceed?</source>
        <translation>La preparacion de una cartograma para una capa vectorial en sistema referencial de coordenadas geográficas no siempre da buenos resultados. Recommendamos convertir la capa por un sistema de coordenadas proyectadas.

¿Continuar de toda manera?</translation>
    </message>
</context>
<context>
    <name>CartogramWorker</name>
    <message>
        <location filename="../cartogram_worker.py" line="103"/>
        <source>Iteration {i}/{mI} for field â{fN}â</source>
        <translation type="obsolete">Iteración {i}/{mI} por atributo «{fN}»</translation>
    </message>
</context>
</TS>
