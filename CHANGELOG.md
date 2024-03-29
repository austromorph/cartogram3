Change Log 
==========
* __3.1.5__ (2022-09-21):
    * detect NULL values in input data set, prompt user (#39)
    * new UI for warnings/errors (QgsMessageBar within plugin dialog)
* __3.1.4__ (2022-04-12):
    * run on even older Python versions (issue #38)
* __3.1.3__ (2022-02-21):
    * run on old-ish Python versions (relax min. version)
* __3.1.2__ (2022-01-12):
    * solved half of issue 29 (no progress on certain input layers)
    * added warning dialog concerning the other half of issue 29
    * updated translations
    * moved batch operations to processing toolbox (simplified plugin dialog)
    * a few smaller fixes
* __3.1.1__ (2021-12-16):
    * fixed regressions (issues 24, 27; residual error reporting, cancel button)
    * progress bar now more fine-grained
* __3.1.0__ (2021-12-10):
    * fix issues 22, 23 (segfaults on QGIS>=3.20, on MacOS and Windows)
    * new: processing toolbox algorithm
    * improved performance
* __3.0.4__ (2019-09-24):
    * fix pending deprecation: `QgsGeometry().set()` marked as deprecated
* __3.0.3__ (2019-03-15):
    * bug fix: hide input layer after computation
* __3.0.2__ (2018-11-26):
    * bug fix: regression introduced in 3.0.1 for older versions (issue #19)
* __3.0.1__ (2018-11-21):
    * bug fix: QgsMapLayer.exportNamedStyle argument order changed (issue #18)
* __3.0.0__ (2018-02-26):
    * adapted to API changes in QGIS core (issues #14 and #15)
* __2.99.5__ (2017-06-14):
    * adapted to API changes in QGIS core (issue #13)
* __2.99.4__ (2017-04-27):
    * adapted to API changes in QGIS core (issue #12)
* __2.99.3__ (2017-03-16):
	* significant performance improvements for large datasets
* __2.99.2__ (2017-02-20):
	* support for QGIS on Microsoft Windows
* __2.99.1__ (2017-02-18):
	* added sample data
	* added German, Spanish & Danish translation
* __2.99.0__ (2017-02-17):
	* initial release
