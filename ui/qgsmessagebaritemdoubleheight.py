#!/usr/bin/env python3

"""A QgsMessageBarItem that has double the height."""

all = ["QgsMessageBarItemDoubleHeight"]


from qgis.gui import QgsMessageBarItem
from qgis.PyQt import QtWidgets


class QgsMessageBarItemDoubleHeight(QgsMessageBarItem):
    """A QgsMessageBarItem that has double the height."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for child in self.children():
            if isinstance(child, QtWidgets.QTextBrowser):
                child.setStyleSheet(
                    child.styleSheet().replace(
                        "max-height: 1.75em;",
                        "max-height: 3.5em;"
                    )
                )
