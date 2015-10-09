# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Name               :Spatial Unit Manager Main Dock Widget
 Description        :An STDM module that enables loading editing and saving
                    layers back to database
                             -------------------
 Date                : 2015-04-08
 Copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
 email                : stdm@unhabitat.org
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

import os

from PyQt4 import uic
from PyQt4.QtGui import QIcon, QMessageBox, QInputDialog, QDockWidget
from PyQt4.QtCore import pyqtSignature
from qgis.core import QgsMapLayerRegistry
from ui_spatial_unit_manager import Ui_SpatialUnitManagerWidget
from gps_tool import GPSToolDialog

from ..data import (
    spatial_tables,
    table_column_names,
    vector_layer,
    geometry_type,
    write_display_name,
    check_if_display_name_exits,
    get_xml_display_name,
    write_changed_display_name
)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_spatial_unit_manager.ui'))


class SpatialUnitManagerDockWidget(QDockWidget, Ui_SpatialUnitManagerWidget):
    """
    Spatial Unit Manager main dock widget, loads all gui functions
    """

    def __init__(self, iface):
        """Constructor."""
        QDockWidget.__init__(self, iface.mainWindow())
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self._populate_layers()
        self._iface = iface
        self._gps_tool_dialog = None
        self._curr_lyr_table = None
        self._curr_lyr_sp_col = None
        self._curr_layer = None

    def _populate_layers(self):
        """
        Method to load spatial layers from STDM database and load them to layer
        combo box
        """
        self.stdm_layers_combo.clear()
        self._stdm_tables = {}
        self.spatial_layers = []
        self.layers_info = []
        for spt in spatial_tables():
            sp_columns = table_column_names(spt, True)
            self._stdm_tables[spt] = sp_columns

            # QMessageBox.information(None,"Title",str(sp_columns))

            # Add spatial columns to combo box
            for sp_col in sp_columns:

                # Get column type and apply the appropriate icon
                geometry_typ = str(geometry_type(spt, sp_col)[0])

                if geometry_typ == "POLYGON":
                    self.icon = QIcon(
                        ":/plugins/stdm/images/icons/layer_polygon.png")
                elif geometry_typ == "LINESTRING":
                    self.icon = QIcon(
                        ":/plugins/stdm/images/icons/layer_line.png")
                elif geometry_typ == "POINT":
                    self.icon = QIcon(
                        ":/plugins/stdm/images/icons/layer_point.png")
                else:
                    self.icon = QIcon(":/plugins/stdm/images/icons/table.png")

                # QMessageBox.information(None,"Title",str(geometry_typ))
                self.stdm_layers_combo.addItem(
                    self.icon, self._format_layer_display_name(
                        sp_col, spt), {"table_name": spt, "col_name": sp_col})

    def _format_layer_display_name(self, col, table):
        """
        Formats layer display name
        :param col: Spatial layer table column name
        :type col: str
        :param table: Spatial layer table name
        :type table: str
        :return: unicode
        """
        return u"{0}.{1}".format(table, col)

    @pyqtSignature("")
    def on_add_to_canvas_button_clicked(self):
        """
        Method to implement add to canvas button
        """
        if self.stdm_layers_combo.count() == 0:

            # Return message that there are no layers
            QMessageBox.warning(None, "No Layers")

        sp_col_info = self.stdm_layers_combo.itemData(
            self.stdm_layers_combo.currentIndex())

        if sp_col_info is None:
            # Message: Spatial column information could not be found
            QMessageBox.warning(
                None, "Spatial Column Layer Could not be found")

        table_name, spatial_column = sp_col_info[
            "table_name"], sp_col_info["col_name"]

        # Used in gpx_table.py
        self._curr_lyr_table = table_name
        self._curr_lyr_sp_col = spatial_column

        self._curr_layer = vector_layer(table_name, geom_column=spatial_column)

        if self._curr_layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(self._curr_layer)

            # Append column name to spatial table
            _current_display_name = str(table_name) + "." + str(spatial_column)

            # Get configuration file display name if it exists
            if check_if_display_name_exits(_current_display_name):
                xml_display_name = get_xml_display_name(_current_display_name)
                self._curr_layer.setLayerName(xml_display_name)

            # Write initial display name as original name of the layer
            elif not check_if_display_name_exits(_current_display_name):
                write_display_name(_current_display_name,
                                   _current_display_name)
                self._curr_layer.setLayerName(_current_display_name)

    @pyqtSignature("")
    def on_set_display_name_button_clicked(self):
        """
        Method to implement set display name button
        """
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layer_map.iteritems():
            if layer == self._iface.activeLayer():
                _name = layer.name()
                display_name, ok = QInputDialog.getText(
                    None, "Change Display Name", "Current Name is {0}".format(
                        layer.originalName()))
                if ok and display_name != "":
                    layer.setLayerName(display_name)
                    write_changed_display_name(_name, display_name)
                elif not ok and display_name == "":
                    layer.originalName()
            else:
                continue

    @pyqtSignature("")
    def on_import_gpx_file_button_clicked(self):
        """
        Method to load import from GPX dialog button
        """
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        if not bool(layer_map):
            QMessageBox.warning(
                None, "STDM", "You must add a layer first, "
                              "from Spatial Unit Manager to import GPX to")
        elif bool(layer_map):
            self._gps_tool_dialog = GPSToolDialog(
                self._iface, self._curr_layer, self._curr_lyr_table,
                self._curr_lyr_sp_col)
            self._gps_tool_dialog.show()
