QGIS3 cartogram3 plugin
=======================

This plugin creates continous cartograms (a.k.a. anamorphic maps) from polygon layers.

It is a port of the [cartogram plugin](https://plugins.qgis.org/plugins/cartogram/) of [Dagbladet Information](https://github.com/informeren/qgis-cartogram) and [Carson Farmer](https://github.com/carsonfarmer/cartogram) to QGIS 3, Python 3 and PyQt5. It also features a few improvements, such as parallel processing (using `multiprocessing`), the option to select multiple variables to batch-produce cartograms, and the possibility to use a maximum total error threshold as a stop condition in addition to the number of iterations.

As its successors, this plugin implements the algorithm proposed by: 

> Dougenik, J. A, N. R. Chrisman, and D. R. Niemeyer. 1985. "An algorithm to construct continuous cartograms." Professional Geographer 37:75-81 

More detailed documention is to be written, in the meantime please refer to the [QGIS 2-Plugin’s documentation](https://github.com/informeren/qgis-cartogram/blob/develop/README.md).

Example
-------

<iframe width="990" height="600" src="https://austromorph.space/kartogramm/population-density/" style="border:none;overflow-y:scroll;    overflow-x:hide;" frameborder=0></iframe>

License
-------

QGIS3 cartogram3
Copyright (C) 2017 Christoph Fink
QGIS Cartogram – a plugin for creating cartograms from polygon layers 
Copyright (C) 2015  Morten Wulff  
Copyright (C) 2013  Carson Farmer

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
