<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de">
<context>
    <name>Cartogram</name>
    <message>
        <location filename="../cartogram3.py" line="112"/>
        <source>&amp;cartogram3</source>
        <translation>&amp;Kartogramm</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="209"/>
        <source>Compute cartogram</source>
        <translation>Kartogramm berechnen</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="111"/>
        <source>&amp;Cartogram</source>
        <translation>&amp;Kartogramm</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="485"/>
        <source>Error</source>
        <translation>Fehler</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="279"/>
        <source>You need at least one polygon vector layer to create a cartogram.</source>
        <translation>Für die Berechnung eines Kartogramms ist mindestens ein Polygon-Vektorlayer erforderlich.</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="357"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="466"/>
        <source>cartogram3 successfully finished computing a cartogram for field ‘{fieldName}’ after {iterations} iterations with {avgError:.2n}% average error remaining.</source>
        <translation>cartogram3: Kartogrammberechnung für Attribut ‚{fieldName}‘ nach {iterations} Durchgängen erfolgreich, verbleibender mittlerer Fehler: {avgError:.2n}%.</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="477"/>
        <source>cartogram3 computation cancelled by user</source>
        <translation>cartogram3: Berechnung vom Benutzer abgebrochen</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="485"/>
        <source>An error occurred during cartogram creation. Please see the ‘Plugins’ section of the message log for details.</source>
        <translation>Fehler bei der Kartogrammberechnung. Einzelheiten im Fehlerprotokoll unter „Plugins“.</translation>
    </message>
    <message>
        <location filename="../cartogram3.py" line="286"/>
        <source>Add sample dataset</source>
        <translation>Beispieldatensatz hinzufügen</translation>
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
        <translation>Input Layer:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="27"/>
        <source>Field(s):</source>
        <translation>Attribut(e):</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="47"/>
        <source>Stop conditions:</source>
        <translation>Bedingungen:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="63"/>
        <source>max. number of iterations:</source>
        <translation>max. Durchgänge:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="83"/>
        <source>max. average error:</source>
        <translation>max. mittlerer Fehler:</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="90"/>
        <source>%</source>
        <translation>%</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="103"/>
        <source>Calculation stops as soon as one condition is met.</source>
        <translation>Die Berechnung endet, sobald eine Bedingung erfüllt ist.</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="30"/>
        <source>To compute cartograms for multiple fields, please use the Processing toolbox batch functionality.</source>
        <translation>Um anamorphe Karten für mehrere Attribute gleichzeitig zu berechnen, verwenden Sie bitte die Batch-Funktion der Processing Toolbox.</translation>
    </message>
    <message>
        <location filename="../ui/cartogram_dialog.ui" line="33"/>
        <source>Field:</source>
        <translation>Attribut:</translation>
    </message>
</context>
<context>
    <name>CartogramProcessingAlgorithm</name>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="59"/>
        <source>Compute cartogram</source>
        <translation>Kartogramm berechnen</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="53"/>
        <source>Vector geometry</source>
        <translation>Vektorgeometrie</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="62"/>
        <source>Input layer</source>
        <translation>Eingabelayer</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="103"/>
        <source>Field</source>
        <translation>Feld</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="77"/>
        <source>max. number of iterations</source>
        <translation>max. Durchgänge:</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="85"/>
        <source>max. average error (%)</source>
        <translation>max. mittlerer Fehler:</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="96"/>
        <source>Output layer</source>
        <translation>Ausgabelayer</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="109"/>
        <source>Iterations needed to meet residual error threshold.</source>
        <translation>Benötigte Durchgänge um Restfehlerwert zu erreichen.</translation>
    </message>
    <message>
        <location filename="../lib/cartogramprocessingalgorithm.py" line="115"/>
        <source>Residual average error.</source>
        <translation>Verbleibende durchschnittliche Abweichung vom Sollwert</translation>
    </message>
</context>
<context>
    <name>CartogramProcessingProvider</name>
    <message>
        <location filename="../lib/cartogramprocessingprovider.py" line="25"/>
        <source>Cartogram</source>
        <translation>Kartogramm</translation>
    </message>
</context>
<context>
    <name>CartogramUserInterfaceMixIn</name>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="94"/>
        <source>Cartogram of {:s}, distorted using ‘{:s}’</source>
        <translation>Kartogramm von „{:s}“, verzerrt nach „{:s}“</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="126"/>
        <source>Cancelled</source>
        <translation>Abgebrochen</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="151"/>
        <source>&amp;Cartogram</source>
        <translation>&amp;Kartogramm</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="156"/>
        <source>Compute cartogram</source>
        <translation>Kartogramm berechnen</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="193"/>
        <source>Add sample dataset</source>
        <translation>Beispieldatensatz hinzufügen</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="185"/>
        <source>Error</source>
        <translation>Fehler</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="187"/>
        <source>You need at least one polygon vector layer to create a cartogram.</source>
        <translation>Für die Berechnung eines Kartogramms ist mindestens ein Polygon-Vektorlayer erforderlich.</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="211"/>
        <source>Computing cartogram</source>
        <translation>Berechne Kartogramm</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="220"/>
        <source>Cancel</source>
        <translation>Abbrechen</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="133"/>
        <source>Geographic CRS</source>
        <translation>Geografisches CRS</translation>
    </message>
    <message>
        <location filename="../lib/cartogramuserinterfacemixin.py" line="133"/>
        <source>Computing a cartogram for a layer with a geographic CRS might not yield best results (consider reprojecting the layer to a projected coordinate system). 

Do you want to proceed?</source>
        <translation>Die Kartogrammberechnung für einen Layer mit geografischem Koordinatenreferenzsystem gelingt nicht immer (wir empfehlen, den Layer in ein projiziertes Referenzsystem umzurechnen).

Trotzdem fortfahren?</translation>
    </message>
</context>
<context>
    <name>CartogramWorker</name>
    <message>
        <location filename="../cartogram_worker.py" line="103"/>
        <source>Iteration {i}/{mI} for field ‘{fN}’</source>
        <translation>Durchgang {i}/{mI} für Attribut ‚{fN}‘</translation>
    </message>
</context>
</TS>
